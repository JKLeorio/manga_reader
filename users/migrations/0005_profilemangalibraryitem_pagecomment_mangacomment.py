# Generated by Django 4.2.1 on 2023-08-31 17:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ImageLib', '0006_genre_manga_genres'),
        ('users', '0004_rename_image_user_avatar'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfileMangaLibraryItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[(1, 'featured_manga'), (2, 'closed_manga'), (3, 'read_manga'), (4, 'abandoned_manga'), (5, 'planned_manga')], max_length=255, verbose_name='Статус')),
                ('manga', models.ManyToManyField(to='ImageLib.manga', verbose_name='Избранная манга')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Владелец')),
            ],
        ),
        migrations.CreateModel(
            name='PageComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.CharField(max_length=777, verbose_name='Комментарий')),
                ('date_of_creation', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('likes', models.PositiveIntegerField(default=0, verbose_name='Количество согласных')),
                ('dislikes', models.PositiveIntegerField(default=0, verbose_name='Количество не согласных')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор комментария')),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ImageLib.page', verbose_name='манга')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MangaComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.CharField(max_length=777, verbose_name='Комментарий')),
                ('date_of_creation', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('likes', models.PositiveIntegerField(default=0, verbose_name='Количество согласных')),
                ('dislikes', models.PositiveIntegerField(default=0, verbose_name='Количество не согласных')),
                ('manga', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ImageLib.manga', verbose_name='манга')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Автор комментария')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
