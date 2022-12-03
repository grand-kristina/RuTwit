from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Модель для групп."""
    title = models.CharField(max_length=200, verbose_name="Заголовок группы")
    slug = models.SlugField(unique=True, verbose_name="слаг для урла")
    description = models.TextField(verbose_name="Описание группы")

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return f"{self.title}"


class Post(models.Model):
    """Модель постов."""
    text = models.TextField(verbose_name="Текст поста", help_text="Введите пожалуйста текст вашего поста")
    pub_date = models.DateTimeField(verbose_name="Дата публикации", auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts", verbose_name="Автор поста"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name="posts",
        blank=True,
        null=True,
        verbose_name="Группа, в которой находится пост",
        help_text="Выберите пожалуйста группу"
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return self.text[:15]