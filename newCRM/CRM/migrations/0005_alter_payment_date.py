# Generated by Django 3.2 on 2022-04-03 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CRM', '0004_alter_lesson_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='date',
            field=models.DateField(),
        ),
    ]
