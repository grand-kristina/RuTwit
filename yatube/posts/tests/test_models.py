from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.client = Client()
        cls.client.force_login(cls.user)
        cls.post = Post.objects.create(
            text='1234567891234567', author=cls.user
        )
        cls.group = Group.objects.create(
            title='Test title',
            description='Test description',
            slug='test-slug'
        )

    def test_verbose_name(self):
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'group': 'Группа, в которой находится пост',
        }

        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите пожалуйста текст вашего поста',
            'group': 'Выберите пожалуйста группу',
        }

        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_group_object_name_is_title_field(self):
        group = PostModelTest.group

        self.assertEqual(str(group), group.title)

    def test_post_object_name_is_shortened_text_field(self):
        post = PostModelTest.post

        self.assertEqual(str(post), post.text[:15])

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        instances = (
            (self.group, self.group.title),
            (self.post, self.post.text[:15]),
        )

        for instance, expected_name in instances:
            with self.subTest(instance=instance):
                self.assertEqual(str(instance), expected_name)
