from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.dispatch import receiver
from django.db.models.signals import post_save
from uuid import uuid4
from datetime import datetime, timedelta, date
import os
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

"""
User
"""
class UserManager(BaseUserManager):

    def create_user(self, email, password=None):
        if not email:
            raise ValueError('メールアドレスを入力してください')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='メールアドレス',
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email


"""
UserActivateToken
"""
class UserActivateTokensManager(models.Manager):

    def activate_user_by_token(self, token):
        user_activate_token = self.filter(
            token=token,
            expired_at__gte=datetime.now()
        ).first()
        user = user_activate_token.user
        user.is_active = True
        user.save()


class UserActivateToken(models.Model):
    user = models.ForeignKey(
        'User', on_delete=models.CASCADE
    )
    token = models.UUIDField(db_index=True)
    expired_at = models.DateTimeField()

    objects = UserActivateTokensManager()

    class Meta:
        db_table = 'user_activate_token'

    def __str__(self):
        return self.user.email


"""
Profile
"""
def upload_image_to(instance, filename):
    image_id = str(instance.user.id)
    return os.path.join('account', 'user_image', image_id, filename)

class Profile(models.Model):
    user = models.OneToOneField(
        User, primary_key=True, on_delete=models.CASCADE)

    username = models.CharField(
        verbose_name='ユーザー名',
        max_length=50,
        default='Anonymous user',
        blank=True,
        )

    introduction = models.CharField(
        verbose_name='自己PR',
        max_length=255,
        default='',
        null=True,
        blank=True
        )

    birth = models.DateField(
        verbose_name='生年月日',
        null=True,
        blank=True
        )
    @property
    def age(self):
        if self.birth:
            today = date.today()
            return today.year - self.birth.year - ((today.month, today.day) < (self.birth.month, self.birth.day))
        else:
            return

    image = models.ImageField(
        verbose_name='アイコン画像',
        upload_to=upload_image_to,
        default='',
        null=True,
        blank=True
        )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


"""
signal
"""
# Signup
@receiver(post_save, sender=User)
def publish_token(sender, instance, **kwargs):
    if not instance.is_active:
        user_activate_token = UserActivateToken.objects.create(
            user=instance,
            token=str(uuid4()),
            expired_at=datetime.now() + timedelta(days=1),
        )

        subject = 'Thanks signup new your account'
        body = render_to_string(
            'account/mail_text/signup.txt', context={
                'user_activate_token': user_activate_token.token
            }
        )

        from_email = ['admin@test.com']
        to = [instance.email]

        email = EmailMessage(
            subject,
            body,
            from_email,
            to,
        )
        email.send()


@receiver(post_save, sender=User)
def create_profile(sender, **kwargs):
    if kwargs['created']:
        Profile.objects.create(user=kwargs['instance'])
