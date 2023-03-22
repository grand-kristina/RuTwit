from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth_user')
        cls.group = Group.objects.create(
            title='test title',
            description='Test description',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            text='Test text', author=cls.user, group=cls.group
        )
        cls.post_url = f'/{cls.user.username}/{cls.post.id}/'
        cls.post_edit_url = f'/{cls.user.username}/{cls.post.id}/edit/'
        cls.public_urls = (
            ('/posts/', 'posts.html'),
            (f'/group/{cls.group.slug}/', 'group.html'),
            (f'/{cls.user.username}/', 'profile.html'),
            (cls.post_url, 'post.html'),
        )
        cls.private_urls = (
            ('/new/', 'new_post.html'),
            (cls.post_edit_url, 'new_post.html')
        )

    def setUp(self):
        self.unauthorized_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)
        cache.clear()

    def test_public_urls_work(self):
        for url, _ in PostsURLTests.public_urls:
            with self.subTest(url=url):
                response = self.unauthorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unauth_user_cannot_access_private_urls(self):
        login_url = reverse('login')

        for url, _ in PostsURLTests.private_urls:
            with self.subTest(url=url):
                target_url = f'{login_url}?next={url}'

                response = self.unauthorized_client.get(url)

                self.assertRedirects(response, target_url)

    def test_authenticated_author_can_access_private_urls(self):
        for url, _ in PostsURLTests.private_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)

                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_public_urls_use_correct_templates(self):
        for url, template in PostsURLTests.public_urls:
            with self.subTest(url=url):
                response = self.unauthorized_client.get(url)

                self.assertTemplateUsed(response, template)

    def test_create_and_edit_urls_use_correct_template_for_post_author(self):
        for url, template in PostsURLTests.private_urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)

                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_non_author_cannot_edit_post(self):
        non_author = User.objects.create_user(username='non_author')
        not_author_client = Client()
        not_author_client.force_login(non_author)

        response = not_author_client.get(PostsURLTests.post_edit_url)

        self.assertRedirects(response, PostsURLTests.post_url)

    def test_server_responds_404_for_unexisted_page(self):
        response = self.authorized_client.get('/unexisted-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
