import shutil
import tempfile

from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class TestPosts(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Test group',
            slug='test-group',
            description='test description'
        )
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            text='Test post',
            author=TestPosts.user,
            group=TestPosts.group
        )

        post_args = (cls.user.username, cls.post.id)
        cls.index_url = ('index', 'index.html', None)
        cls.group_url = ('group', 'group.html', (cls.group.slug,))
        cls.profile_url = ('profile', 'profile.html', (cls.user.username,))
        cls.post_url = ('post', 'post.html', post_args)
        cls.new_post_url = ('new_post', 'new_post.html', None)
        cls.edit_post_url = ('post_edit', 'new_post.html', post_args)
        cls.paginated_urls = (
            cls.index_url,
            cls.group_url,
            cls.profile_url
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.unauthorized_client = Client()
        self.authorized_client.force_login(TestPosts.user)

        cache.clear()

    def check_context_contains_page_or_post(self, context, post=False):
        if post:
            self.assertIn('post', context)
            post = context['post']
        else:
            self.assertIn('page', context)
            post = context['page'][0]
        self.assertEqual(post.author, TestPosts.user)
        self.assertEqual(post.pub_date, TestPosts.post.pub_date)
        self.assertEqual(post.text, TestPosts.post.text)
        self.assertEqual(post.group, TestPosts.post.group)

    def test_correct_templates_used_for_reversed_urls(self):
        """
        Тест, проверяющий какие вызываются шаблоны, при вызове вьюхи
        через name.
        """
        extra_urls = (
            TestPosts.post_url, TestPosts.edit_post_url, TestPosts.new_post_url
        )
        for name, template, args in (TestPosts.paginated_urls + extra_urls):
            with self.subTest(name=name):
                response = self.authorized_client.get(
                    reverse(name, args=args),
                )
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_index_page_context_is_correct(self):
        url, _, args = TestPosts.index_url
        response = self.unauthorized_client.get(reverse(url, args=args))

        self.check_context_contains_page_or_post(response.context)

    def test_profile_page_context_is_correct(self):
        url, _, args = TestPosts.profile_url
        response = self.unauthorized_client.get(reverse(url, args=args))

        self.check_context_contains_page_or_post(response.context)

        self.assertIn('author', response.context)
        self.assertEqual(response.context['author'], TestPosts.user)

    def test_post_page_context_is_correct(self):
        url, _, args = TestPosts.post_url
        response = self.unauthorized_client.get(reverse(url, args=args))

        self.check_context_contains_page_or_post(response.context, post=True)

        self.assertIn('author', response.context)
        self.assertEqual(response.context['author'], TestPosts.user)

        self.assertIn('posts_count', response.context)
        self.assertEqual(
            response.context['posts_count'], TestPosts.user.posts.count()
        )

    def test_new_post_and_edit_post_pages_context_is_correct(self):
        urls = (
            TestPosts.new_post_url,
            TestPosts.edit_post_url
        )

        for name, _, args in urls:
            with self.subTest(name=name):
                is_edit_value = bool(name == 'post_edit')

                response = self.authorized_client.get(reverse(name, args=args))

                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], PostForm)

                self.assertIn('is_edit', response.context)
                is_edit = response.context['is_edit']
                self.assertIsInstance(is_edit, bool)
                self.assertEqual(is_edit, is_edit_value)

    def test_group_page_context_is_correct(self):
        url, _, args = TestPosts.group_url
        response = self.unauthorized_client.get(reverse(url, args=args))

        self.check_context_contains_page_or_post(response.context)

        self.assertIn('group', response.context)
        group = response.context['group']
        self.assertEqual(group.title, TestPosts.group.title)
        self.assertEqual(group.description, TestPosts.group.description)

    def test_other_group_does_not_have_the_post(self):
        Post.objects.create(
            text='test', author=TestPosts.user, group=TestPosts.group
        )
        group = Group.objects.create(
            title='Group 2',
            slug='group-2',
            description='group 2'
        )

        response = self.unauthorized_client.get(
            reverse('group', args=(group.slug,))
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context['paginator'].count, 0)

    def test_paginator_in_pages_with_posts(self):
        post_count = Post.objects.count()
        paginator_amount = 10
        second_page_amount = post_count + 3
        posts = [
            Post(
                text=f'text {num}', author=TestPosts.user,
                group=TestPosts.group
            ) for num in range(1, paginator_amount + second_page_amount)
        ]
        Post.objects.bulk_create(posts)

        pages = (
            (1, paginator_amount),
            (2, second_page_amount)
        )

        for name, _, args in TestPosts.paginated_urls:
            for page, count in pages:
                with self.subTest(name=name, page=page):
                    response = self.unauthorized_client.get(
                        reverse(name, args=args), {'page': page}
                    )

                    self.assertEqual(
                        len(response.context.get('page').object_list), count
                    )

    def test_post_with_image_appears_in_pages(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif')
        post = Post.objects.create(
            text='abc',
            author=self.user,
            group=self.group,
            image=uploaded,
        )

        urls = (
            reverse('index'),
            reverse('profile', args=(self.user.username,)),
            reverse('post', args=(self.user.username, post.id)),
            reverse('group', args=(self.group.slug,))
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertContains(response, '<img')

    def test_cache_works(self):
        posts_count = Post.objects.count()
        post = Post.objects.create(
            text='test',
            author=self.user,
            group=self.group
        )
        index = reverse('index')
        response = self.authorized_client.get(index)
        cached_response_content = response.content
        paginator = response.context.get('paginator')

        self.assertEqual(paginator.count, posts_count + 1)
        post_in_page = response.context['page'][0]
        self.assertEqual(post_in_page.text, post.text)
        self.assertEqual(post_in_page.author, post.author)
        self.assertEqual(post_in_page.group, post.group)

        post.delete()

        response = self.authorized_client.get(index)
        self.assertEqual(cached_response_content, response.content)

        cache.clear()

        response = self.authorized_client.get(index)
        self.assertNotEqual(cached_response_content, response.content)

    def test_authorized_user_can_follow(self):
        new_user = User.objects.create_user(username='test')

        response = self.authorized_client.get(
            reverse('profile_follow', args=(new_user.username,)),
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Follow.objects.count(), 1)
        follow = Follow.objects.first()
        self.assertEqual(follow.user, self.user)
        self.assertEqual(follow.author, new_user)

    def test_authorized_user_can_unfollow(self):
        author = User.objects.create_user(username='test')
        Follow.objects.create(user=self.user, author=author)

        response = self.authorized_client.get(
            reverse('profile_unfollow', args=(author.username,)),
            follow=True
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Follow.objects.count(), 0)

    def test_post_appears_in_follow_page_for_followed_author(self):
        author = User.objects.create_user(username='test')
        Follow.objects.create(user=self.user, author=author)
        post = Post.objects.create(
            author=author,
            text='abc',
            group=self.group
        )

        follow_page = reverse('follow_index')

        response = self.authorized_client.get(follow_page)

        post_in_page = response.context['page'][0]

        self.assertEqual(post_in_page, post)
        self.assertEqual(post_in_page.author, author)
        self.assertEqual(post_in_page.pub_date, post.pub_date)
        self.assertEqual(post_in_page.text, post.text)
        self.assertEqual(post_in_page.group, post.group)

    def test_post_does_not_appear_in_follow_page_if_author_is_not_followed(
            self
    ):
        self.assertEqual(Follow.objects.count(), 0)

        author = User.objects.create_user(username='test')
        Post.objects.create(
            author=author,
            text='abc',
            group=self.group
        )
        follow_page = reverse('follow_index')

        response = self.authorized_client.get(follow_page)

        self.assertEqual(response.context['paginator'].count, 0)

    def test_authorized_user_can_publish_comment(self):
        post = Post.objects.create(
            author=self.user,
            text='abc',
            group=self.group
        )
        response = self.authorized_client.post(
            reverse('add_comment', args=(self.user.username, post.id)),
            data={'text': 'hello'},
            follow=True
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()

        self.assertEqual(comment.text, 'hello')
        self.assertEqual(comment.post, post)
        self.assertEqual(comment.author, self.user)

    def test_unauthorized_user_cant_publish_comment(self):
        post = Post.objects.create(
            author=self.user,
            text='abc',
            group=self.group
        )
        self.unauthorized_client.post(
            reverse('add_comment', args=(self.user.username, post.id)),
            data={'text': 'hello'},
            follow=True
        )

        self.assertEqual(Comment.objects.count(), 0)
