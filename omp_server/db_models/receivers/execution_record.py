import datetime

from django.dispatch import receiver
from django.db.models.signals import post_save

from db_models.models import ExecutionRecord, MainInstallHistory, \
    UpgradeHistory, RollbackHistory
from db_models.models.execution import StateChoices


def create_execution_record(instance, created=False, *args, **kwargs):
    module = instance.__class__.__name__
    obj, _ = ExecutionRecord.objects.get_or_create(
        module=module,
        module_id=instance.module_id
    )
    old_state = obj.state
    state = f"{module.upper()}_{instance.execution_record_state}"
    obj.state = getattr(StateChoices, state)
    if isinstance(instance.operator, str):
        obj.operator = instance.operator
    else:
        obj.operator = instance.operator.username
    obj.created = instance.created
    if ("SUCCESS" in obj.state or "FAIL" in obj.state) and \
            obj.state != old_state:
        obj.end_time = instance.modified
    obj.count = instance.operate_count()
    obj.save()


@receiver(post_save, sender=MainInstallHistory)
def install_execution_record(sender, instance, *args, **kwargs):
    create_execution_record(instance, *args, **kwargs)


@receiver(post_save, sender=UpgradeHistory)
def upgrade_execution_record(sender, instance, created, *args, **kwargs):
    create_execution_record(instance, created, *args, **kwargs)


@receiver(post_save, sender=RollbackHistory)
def rollback_execution_record(sender, instance, created, *args, **kwargs):
    create_execution_record(instance, created, *args, **kwargs)
