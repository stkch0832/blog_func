from django.db import models
from django.contrib.auth import get_user_model
import os

User = get_user_model()

"""
Post
"""
def upload_image_to(instance, filename):
    post_id = str(instance.user.id)
    return os.path.join('blog', 'upload_image', post_id, filename)

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    title = models.CharField(
        verbose_name='タイトル',
        max_length=30
        )

    content = models.TextField(
        verbose_name='本文',
        max_length=500
        )

    image = models.ImageField(
        verbose_name='投稿画像',
        upload_to=upload_image_to,
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(
        verbose_name='作成日時',
        auto_now_add=True,
        )

    updated_at = models.DateTimeField(
        verbose_name='更新日時',
        auto_now=True,
        )

    class Meta:
        db_table = 'post'

    def __str__(self):
        return self.title
