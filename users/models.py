import uuid
import os

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone
from django.dispatch import receiver

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, nickname, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(nickname, email, password, **extra_fields)

    def create_superuser(self, nickname, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(nickname, email, password, **extra_fields)

    def _create_user(self, nickname, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, nickname=nickname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user


def user_directory_path(instance, filename):
    extension = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{extension}"
    return f"profiles/{timezone.now().date().strftime('%Y/%m/%d')}/{filename}"


class User(AbstractBaseUser, PermissionsMixin):
    nickname = models.CharField(
        max_length=255,
        help_text="Full name/alias/nickname as you would usually sign your emails, "
                  "e.g. John Johnson or Lord Demogorgon."
    )
    email = models.EmailField(
        unique=True,
        help_text="The email address of the main label. It will be needed for logging in."
    )
    avatar = models.ImageField(upload_to=user_directory_path, blank=True, verbose_name="avatar")
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    objects = UserManager()

    def __str__(self):
        return f"{self.nickname} ({self.email})"

    def delete(self, using=None, keep_parents=False):
        self.image.delete()
        super().delete()


    class Meta:
        verbose_name = 'Системный пользователь'
        verbose_name_plural = "Системные пользователи"



@receiver(models.signals.pre_save, sender=User)
def auto_delete_file_on_change(sender, instance, **kwargs):

    if not instance.pk:
        return False

    try:
        old_file = User.objects.get(pk=instance.pk).avatar
    except User.DoesNotExist:
        return False

    if old_file:
        models.signals.pre_save.disconnect(auto_delete_file_on_change, sender=sender)
        old_file.delete()
        models.signals.pre_save.connect(auto_delete_file_on_change, sender=sender)
        
