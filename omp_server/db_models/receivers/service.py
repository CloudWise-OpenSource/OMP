from django.db.models.signals import pre_delete
from django.dispatch import receiver

from db_models.mixins import UpgradeStateChoices, RollbackStateChoices
from db_models.models import Service, MainInstallHistory, \
    ExecutionRecord, UpgradeHistory, RollbackHistory, UpgradeDetail, \
    RollbackDetail


def update_upgrade_history(history, union_server):
    UpgradeDetail.objects.filter(
        union_server=union_server).delete()
    details = history.upgradedetail_set.exclude(
        upgrade_state=UpgradeStateChoices.UPGRADE_SUCCESS
    ).exclude(union_server=union_server)
    if not details.exists():
        history.upgrade_state = UpgradeStateChoices.UPGRADE_SUCCESS
        history.save()


def update_rollback_history(history, union_server):
    RollbackDetail.objects.filter(
        upgrade__union_server=union_server).delete()
    details = history.rollbackdetail_set.exclude(
        rollback_state=RollbackStateChoices.ROLLBACK_SUCCESS
    ).exclude(upgrade__union_server=union_server)
    if not details.exists():
        history.rollback_state = RollbackStateChoices.ROLLBACK_SUCCESS
        history.save()


@receiver(pre_delete, sender=Service)
def update_execution_record(sender, instance, *args, **kwargs):
    # models.SET_NULL --> models.SET() ?
    filter_keys = [
        (MainInstallHistory, "detailinstallhistory__service"),
        (RollbackHistory, "rollbackdetail__upgrade__service"),
        (UpgradeHistory, "upgradedetail__service"),
    ]
    if instance.service.app_name == "hadoop" and instance.service_split == 2:
        Service.split_objects.filter(
            ip=instance.ip,
            service__app_name="hadoop"
        ).delete()

    union_server = f"{instance.ip}-{instance.service.app_name}"

    for model_cls, filter_key in filter_keys:
        history = model_cls.objects.filter(**{filter_key: instance}).first()
        if not history:
            continue
        execution_record = ExecutionRecord.objects.filter(
            module=history.__class__.__name__,
            module_id=history.module_id
        ).first()
        if not execution_record:
            continue
        execution_record.count = history.operate_count([instance.id])
        execution_record.save()
        if model_cls.__name__ == "RollbackHistory" and \
                history.rollback_state != RollbackStateChoices.ROLLBACK_SUCCESS:
            update_rollback_history(history, union_server)
        if model_cls.__name__ == "UpgradeHistory" and \
                history.upgrade_state != UpgradeStateChoices.UPGRADE_SUCCESS:
            update_upgrade_history(history, union_server)
