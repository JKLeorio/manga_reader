# Generated by Django 4.2.1 on 2023-08-31 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ImageLib', '0005_alter_volume_manga'),
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'Жанр',
                'verbose_name_plural': 'Жанры',
            },
        ),
        migrations.AddField(
            model_name='manga',
            name='genres',
            field=models.ManyToManyField(to='ImageLib.genre', verbose_name='Жанры'),
        ),
    ]
