# Generated by Django 3.2 on 2022-04-03 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0003_client_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='date',
            field=models.DateField(),
        ),
    ]
