# Generated by Django 3.1.4 on 2021-12-02 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db_models', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='service_status',
            field=models.IntegerField(choices=[(0, '正常'), (1, '启动中'), (2, '停止中'), (3, '重启中'), (4, '停止'), (5, '未知'), (6, '安装中'), (7, '安装失败'), (8, '待安装')], default=5, help_text='服务状态', verbose_name='服务状态'),
        ),
    ]
