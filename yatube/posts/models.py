from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """Модель для групп."""

    # Тут смотрим, чтобы max_length не был слишком маленький,
    # студенты любят тут написать что-нибудь около 10 :)
    title = models.CharField(max_length=200, verbose_name="Заголовок группы")
    slug = models.SlugField(unique=True, verbose_name="слаг для урла")
    description = models.TextField(verbose_name="Описание группы")

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    # Можно лучше:
    # Добавляем __str__.
    # В постах можно не добавлять, так как там нет чего-то
    # короткого и содержательного как title здесь.

    # Меняем тут на просто self.title, тк это будет отображаться в селекте
    # в форме
    def __str__(self):
        return f"{self.title}"


class Post(models.Model):
    """Модель постов."""

    text = models.TextField("Текст поста")
    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts", verbose_name="Автор поста"
    )
    group = models.ForeignKey(
        Group,
        # Надо исправить:
        # Объясняем, почему тут SET_NULL
        on_delete=models.SET_NULL,
        related_name="posts",
        blank=True,
        null=True,
        verbose_name="Группа, в которой находится пост",
    )

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
