import logging
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, \
    ALL_COMPLETED

from celery import shared_task

from db_models.mixins import UpgradeStateChoices, RollbackStateChoices
from db_models.models import UpgradeHistory, RollbackHistory, \
    RollbackDetail, Maintain
from promemonitor.alertmanager import Alertmanager
from service_upgrade.handler.base import load_upgrade_detail, \
    handler_pipeline, load_rollback_detail
from service_upgrade.handler.rollback_handler import rollback_handlers
from service_upgrade.handler.upgrade_handler import upgrade_handlers
from utils.parse_config import BASIC_ORDER, THREAD_POOL_MAX_WORKERS

logger = logging.getLogger(__name__)


def get_service_order():
    # 获取配置文件层次，解析成dict
    service_layer = {}
    for index, services in BASIC_ORDER.items():
        for service in services:
            service_layer[service] = index
    return service_layer


def computer_operation_sorted(details):
    # 通过服务依赖确定服务升级、回滚顺序
    order_layer_details = {}
    service_layer = get_service_order()
    max_index = max(service_layer.values()) + 1
    union_service = set()
    for detail in details:
        if isinstance(detail, RollbackDetail):
            union_server = detail.upgrade.union_server
            app_name = detail.upgrade.current_app.app_name
            extend_fields = detail.upgrade.current_app.extend_fields
        else:
            union_server = detail.union_server
            app_name = detail.current_app.app_name
            extend_fields = detail.current_app.extend_fields
        if union_server in union_service:
            continue
        union_service.add(union_server)
        s_i = service_layer.get(app_name, None)
        if s_i is None:
            s_i = max_index + int(extend_fields.get("level", 0))
        if s_i not in order_layer_details:
            order_layer_details[s_i] = [detail]
        else:
            order_layer_details[s_i].append(detail)
    # [(0, [detail1]), (1, [detail2, detail3])]
    return sorted(order_layer_details.items(), key=lambda x: x[0])


def set_alert_maintain(env_name):
    try:
        has_maintain = Maintain.objects.filter(
            matcher_name="env", matcher_value=env_name
        ).exists()
        if not has_maintain:
            return Alertmanager().set_maintain_by_env_name(env_name)
    except Exception as e:
        logger.error(f"进入维护模式失败：{str(e)}")
    return None


@shared_task
def upgrade_service(upgrade_history_id):
    history = UpgradeHistory.objects.filter(id=upgrade_history_id).first()
    if not history:
        logger.error(f"未找到id为{upgrade_history_id}的升级操作！")
        return
    if history.upgrade_state not in {
        UpgradeStateChoices.UPGRADE_WAIT,
        UpgradeStateChoices.UPGRADE_FAIL
    }:
        logger.error(f"升级记录状态为{history.get_upgrade_state_display()}，不可升级！")
        return
    # 排除hadoop等多余服务，升级只升一次
    if history.upgrade_state != UpgradeStateChoices.UPGRADE_ING:
        history.upgrade_state = UpgradeStateChoices.UPGRADE_ING
        history.save()

    upgrade_details = history.upgradedetail_set.exclude(
        upgrade_state=UpgradeStateChoices.UPGRADE_SUCCESS
    ).exclude(has_rollback=True)

    order_layer_details = computer_operation_sorted(upgrade_details)
    set_alert_maintain(history.env.name)
    with ThreadPoolExecutor(THREAD_POOL_MAX_WORKERS) as executor:
        upgrade_state = UpgradeStateChoices.UPGRADE_SUCCESS
        for sort, details in order_layer_details:
            all_task = []
            for detail in details:
                upgrade_args = load_upgrade_detail(detail)
                future_obj = executor.submit(
                    handler_pipeline, upgrade_handlers, upgrade_args)
                all_task.append(future_obj)
            wait(all_task, return_when=ALL_COMPLETED)
            for future in as_completed(all_task):
                upgrade_args = future.result()
                if upgrade_args is None:
                    upgrade_state = UpgradeStateChoices.UPGRADE_FAIL
                    break
            if upgrade_state == UpgradeStateChoices.UPGRADE_FAIL:
                break
    history.upgrade_state = upgrade_state
    history.save()


@shared_task
def rollback_service(rollback_history_id):
    history = RollbackHistory.objects.filter(id=rollback_history_id).first()
    if not history:
        logger.error(f"未找到id为{rollback_history_id}的回滚操作！")
        return
    if history.rollback_state not in {
        RollbackStateChoices.ROLLBACK_WAIT,
        RollbackStateChoices.ROLLBACK_FAIL
    }:
        logger.error(f"回滚记录状态为{history.get_rollback_state_display()}，不可回滚！")
        return
    if history.rollback_state != RollbackStateChoices.ROLLBACK_ING:
        history.rollback_state = RollbackStateChoices.ROLLBACK_ING
        history.save()

    # 排除hadoop等多余服务，升级只升一次
    rollback_details = history.rollbackdetail_set.exclude(
        rollback_state=RollbackStateChoices.ROLLBACK_SUCCESS
    )
    order_layer_details = computer_operation_sorted(rollback_details)

    set_alert_maintain(history.env.name)

    with ThreadPoolExecutor(THREAD_POOL_MAX_WORKERS) as executor:
        rollback_state = RollbackStateChoices.ROLLBACK_SUCCESS
        for sort, details in order_layer_details:
            all_task = []
            for detail in details:
                rollback_args = load_rollback_detail(detail)
                future_obj = executor.submit(
                    handler_pipeline, rollback_handlers, rollback_args)
                all_task.append(future_obj)
            wait(all_task, return_when=ALL_COMPLETED)
            for future in as_completed(all_task):
                rollback_args = future.result()
                if rollback_args is None:
                    rollback_state = RollbackStateChoices.ROLLBACK_FAIL
                    break
            if rollback_state == RollbackStateChoices.ROLLBACK_FAIL:
                break
    history.rollback_state = rollback_state
    history.save()
