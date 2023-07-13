from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.models import PublishedAndCreatedModel

User = get_user_model()

TEXT_LIMIT = 20


class Location(PublishedAndCreatedModel):
    name = models.CharField(max_length=256,
                            verbose_name='Название места')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name[:TEXT_LIMIT]


class Category(PublishedAndCreatedModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL;'
            'разрешены символы латиницы, цифры, '
            'дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:TEXT_LIMIT]


class Post(PublishedAndCreatedModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(default=timezone.now,
                                    verbose_name='Дата и время публикации',
                                    help_text=('Если установить дату и время '
                                               'в будущем — можно делать '
                                               'отложенные публикации.'))
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               verbose_name='Автор публикации')
    location = models.ForeignKey(Location,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 blank=True,
                                 verbose_name='Местоположение')
    category = models.ForeignKey(Category,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 verbose_name='Категория')
    image = models.ImageField('Фото', upload_to='post_images', blank=True)

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title[:TEXT_LIMIT]


class Comment(models.Model):
    text = models.TextField('Комментарий')
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comment')
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return self.text[:TEXT_LIMIT]
