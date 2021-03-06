# Generated by Django 3.2 on 2022-07-01 09:08

import CRM.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0007_auto_20220504_1257'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='group',
            field=models.ForeignKey(default=CRM.models.getDefaultGroup, on_delete=django.db.models.deletion.PROTECT, to='CRM.group'),
        ),
        # migrations.CreateModel(
        #     name='Salary',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('date', models.DateField()),
        #         ('value', models.FloatField(default=0)),
        #         ('note', models.CharField(default='', max_length=200)),
        #         ('teacher', models.ForeignKey(default=CRM.models.getDefaultTeacher, on_delete=django.db.models.deletion.PROTECT, to='CRM.teacher')),
        #     ],
        # ),
    ]
