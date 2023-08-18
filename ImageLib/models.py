from django.db import models
from django.conf import settings
import datetime

YEAR_CHOICES = [(r, r) for r in range(1945, datetime.date.today().year + 1)]


def Manga_cover_directory_path(instance, filename):
    extension = filename.split('.')[-1]
    manga_name = instance.name
    filename = f"{manga_name}_cover.{extension}"
    return f"{manga_name}/cover/{filename}"


def Volume_cover_directory_path(instance, filename):
    extension = filename.split('.')[-1]
    manga_name = instance.manga.name
    filename = f"{manga_name}_{instance.number}.{extension}"
    return f"{manga_name}/Vol_{instance.number}/Cover/{filename}"


def Chapter_directory_path(instance, filename):
    extension = filename.split('.')[-1]
    manga_name = instance.chapter.volume.manga.name
    volume = instance.chapter.volume.number
    filename = f"{instance.number}.{extension}"
    return f"{manga_name}/Vol_{volume}/Ch_{instance.chapter.number}/{filename}"


class Author(models.Model):
    first_name = models.CharField(max_length=255, verbose_name="Имя")
    last_name = models.CharField(max_length=255, verbose_name="Фамилия")
    Date_of_Birth = models.DateField(verbose_name="Дата рождения")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = "Авторы"


class Status(models.Model):
    name = models.CharField(max_length=255, verbose_name="Статус")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = "Статусы"


class ReleaseFormat(models.Model):
    name = models.CharField(max_length=255, verbose_name="Формат выпуска")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'Формат выпуска'
        verbose_name_plural = "Форматы выпуска"


class Painter(models.Model):
    first_name = models.CharField(max_length=255, verbose_name="Имя")
    last_name = models.CharField(max_length=255, verbose_name="Фамилия")
    Date_of_Birth = models.DateField(verbose_name="Дата рождения")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'Художник'
        verbose_name_plural = "Художники"


# class Translator(models.Model):
# 	name = models.CharField(max_length=255, verbose_name = "Название")
# 	description = models.TextField(max_length = 1024, verbose_name = "Описание")
# class Meta:
#     verbose_name = 'Переводчик'
#     verbose_name_plural = "Переводчики"

class Manga(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(max_length=5000, verbose_name="Описание")
    release_year = models.IntegerField(choices=YEAR_CHOICES, default=datetime.datetime.now().year,
                                       verbose_name="Год выпуска")
    status = models.ForeignKey(Status, on_delete=models.CASCADE, verbose_name="Статус")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name="Автор")
    painter = models.ForeignKey(Painter, on_delete=models.CASCADE, verbose_name="Художник")
    release_format = models.ManyToManyField(ReleaseFormat, verbose_name="Формат выпуска")
    manga_cover = models.ImageField(upload_to=Manga_cover_directory_path, verbose_name="Обложка манги")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = "Произведения"


class Volume(models.Model):
    number = models.PositiveSmallIntegerField()
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE,
                              verbose_name="Произведение")

    # Volume_cover = models.ImageField(upload_to = Volume_cover_directory_path, verbose_name = "Обложка тома")

    def __str__(self):
        return f"{self.number}"

    class Meta:
        verbose_name = 'Том'
        verbose_name_plural = "Тома"


class Chapter(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название главы")
    number = models.PositiveSmallIntegerField(verbose_name="Номер главы")
    volume = models.ForeignKey(Volume, on_delete=models.CASCADE, verbose_name="Том")

    # translator = models.ForeignKey(Translator, on_delete = models.CASCADE, "Переводчик")

    def __str__(self):
        return f"{self.number}"

    class Meta:
        verbose_name = 'Глава'
        verbose_name_plural = "Главы"


class Page(models.Model):
    number = models.PositiveSmallIntegerField(verbose_name="Номер страницы")
    image = models.ImageField(upload_to=Chapter_directory_path, verbose_name="Страница")
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, verbose_name="Глава")

    def __str__(self):
        return f"{self.number}"

    class Meta:
        verbose_name = 'Страница'
        verbose_name_plural = "Страницы"
