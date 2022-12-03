import shutil
import tempfile

from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-group',
            description='test description'
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        cache.clear()

    def test_unauth_user_cant_publish_post(self):
        count = Post.objects.count()
        response = self.client.post(
            reverse('posts:post_create'),
            data={'text': 'Test post', 'group': PostFormTests.group.id},
        )
        login_url = reverse('login')
        new_post_url = reverse('posts:post_create')
        target_url = f'{login_url}?next={new_post_url}'
        self.assertRedirects(response, target_url)
        self.assertEqual(Post.objects.count(), count)

    def test_auth_user_can_edit_his_post(self):
        post = Post.objects.create(
            text='test',
            author=self.user,
            group=PostFormTests.group
        )
        new_post_text = 'new text'
        new_group = Group.objects.create(
            title='New Test group',
            slug='new-test-group',
            description='new test description'
        )

        self.authorized_client.post(
            reverse('posts:post_edit', args=(post.id,)),
            data={'text': new_post_text, 'group': new_group.id},
            follow=True,
        )

        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.first()
        self.assertEqual(post.text, new_post_text)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, new_group)

        old_group_response = self.authorized_client.get(
            reverse('posts:group_list', args=(self.group.slug,))
        )

        self.assertEqual(len(old_group_response.context['page_obj']), 0)
