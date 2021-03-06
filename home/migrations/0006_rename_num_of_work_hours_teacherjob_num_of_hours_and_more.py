# Generated by Django 4.0.3 on 2022-04-08 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_remove_academdegree_num_of_work_hours_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teacherjob',
            old_name='num_of_work_hours',
            new_name='num_of_hours',
        ),
        migrations.RemoveField(
            model_name='subject',
            name='hours_num',
        ),
        migrations.AddField(
            model_name='subject',
            name='num_of_sub_in_week',
            field=models.IntegerField(null=True, verbose_name='Количество предметов в неделю'),
        ),
        migrations.AddField(
            model_name='teacher',
            name='is_busy',
            field=models.BooleanField(default=False, verbose_name='Занят ли преподаватель?'),
        ),
    ]
