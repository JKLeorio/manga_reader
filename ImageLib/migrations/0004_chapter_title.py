# Generated by Django 4.2.1 on 2023-07-04 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ImageLib', '0003_alter_manga_release_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='chapter',
            name='title',
            field=models.CharField(default='title', max_length=255, verbose_name='Название главы'),
            preserve_default=False,
        ),
    ]
