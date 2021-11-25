import logging
import traceback

from db_models.models import InspectionHistory, InspectionReport
from inspection.joint_json_report import joint_json_data
from utils.plugin.send_email import ModelSettingEmailBackend, many_send
from utils.prometheus.create_html_tar import create_html_tar
from utils.plugin import send_email as send_email_module

logger = logging.getLogger("server")


def send_email(inspection, emails):
    """
    发送邮件
    :param inspection: 巡检对象
    :param emails: 邮箱列表
    :return:
    """
    if not inspection:
        return False, "无巡检对象"
    inspection_report = InspectionReport.objects.filter(
        inst_id=inspection.id).first()
    if not inspection_report.file_name:
        return False, "未找到巡检报告！"
    inspection.send_email_result = inspection.ING
    inspection.save()
    reason = ""
    try:
        connection = ModelSettingEmailBackend()
        if inspection.inspection_type == "host" or inspection.inspection_type == "service":
            content_name = "SendNormalInspectionEmailContent"
        elif inspection.inspection_type == "deep":
            content_name = "SendDeepInspectionEmailContent"
        else:
            content_name = "SendEmailContent"
        content = getattr(send_email_module, content_name)(inspection)
        fail_user = many_send(connection, content, emails)
    except Exception as e:
        logger.error(f"发送邮件失败， 错误信息：{str(e)}")
        reason = "系统异常，请重试!"
        fail_user = emails
    if fail_user:
        inspection.send_email_result = inspection.FAIL
        reason = "发件失败，请检查smtp邮箱服务器配置！"
    else:
        inspection.send_email_result = inspection.SUCCESS
    inspection.email_fail_reason = reason
    inspection.save()
    return not bool(fail_user), reason


# def create_inspection_html(inspection):
#     """
#     生成巡检报告文件、更新巡检对象信息(重复，不修改发送邮件状态)
#     :param inspection:
#     :return:
#     """
#     if not inspection:
#         return False, "无巡检对象"
#     if inspection.inspection_status != 2:
#         return False, "巡检结果未成功！"
#     report_data = inspection.report_data
#     time_str = inspection.inspection_name.split("-")[1]
#     new_html_dir_name = f"{inspection.__class__.__name__.lower()}-{time_str}"
#     try:
#         state, result = create_html_tar(new_html_dir_name, report_data)
#     except Exception as e:
#         logger.error(f"打包巡检报告发生错误：{str(e)}, 详情为：\n{traceback.format_exc()}")
#         inspection.email_fail_reason = "打包巡检报告发生错误!"
#         inspection.save()
#         return False, "打包巡检报告发生错误!"
#     if not state:
#         inspection.email_fail_reason = result
#         inspection.save()
#         return False, result
#     inspection.file_name = result
#     inspection.save()
#     return True, result


def create_send_inspection_html(inspection):
    """
    生成巡检报告文件、更新巡检对象信息（更新发送邮件状态）
    :param inspection:
    :return:
    """
    if not inspection:
        return False, "无巡检对象"
    if inspection.inspection_status != 2:
        return False, "巡检结果未成功！"
    inspection_report = InspectionReport.objects.filter(inst_id=inspection.id)
    if not inspection_report:
        return False, "未找到巡检报告！"
    report_data = joint_json_data(
        inspection.inspection_type, inspection_report, inspection)
    time_str = inspection.inspection_name.split("-")[1]
    new_html_dir_name = f"{inspection.__class__.__name__.lower()}-{time_str}"
    try:
        state, result = create_html_tar(new_html_dir_name, report_data)
    except Exception as e:
        logger.error(f"打包巡检报告发生错误：{str(e)}, 详情为：\n{traceback.format_exc()}")
        inspection.send_email_result = 0
        inspection.email_fail_reason = "打包巡检报告发生错误!"
        inspection.save()
        return False, "打包巡检报告发生错误!"
    if not state:
        inspection.send_email_result = 0
        inspection.email_fail_reason = result
        inspection.save()
        return False, result
    inspection_report.file_name = result
    inspection.save()
    inspection_report.save()
    return True, result


def send_report_email(inspection_module, inspection_id, emails):
    """
    生成、发送报告
    :param inspection_module: DeepInspection、NormalInspection
    :param inspection_id:
    :param emails: 邮箱list
    :return:
    """
    inspection = InspectionHistory.objects.filter(id=inspection_id).first()
    if not inspection:
        return False, "未找到对应的巡检！"
    if inspection.inspection_status != 2:
        return False, "巡检结果未成功！"
    inspection_report = InspectionReport.objects.filter(
        inst_id=inspection_id).first()
    if not inspection_report:
        return False, "未找到对应的巡检报告！"
    if inspection.send_email_result == 2:
        return False, "正在发送巡检报告，请稍后再试！"
    inspection.send_email_result = 2
    inspection.save()
    if not inspection_report.file_name:
        try:
            state, result = create_send_inspection_html(inspection)
        except Exception as e:
            logger.error(
                f"打包巡检报告发生错误：{str(e)}, 详情为：\n{traceback.format_exc()}")
            inspection.send_email_result = inspection.FAIL
            inspection.email_fail_reason = "打包巡检报告发生错误！"
            inspection.save()
            return False, "打包巡检报告发生错误！"
        if not state:
            return False, result
    try:
        state, email_fail_reason = send_email(inspection, emails)
    except Exception as e:
        logger.error(f"发送邮件发生错误：{str(e)}, 详情为：\n{traceback.format_exc()}")
        return "发送邮件发生错误!"
    return state, email_fail_reason
