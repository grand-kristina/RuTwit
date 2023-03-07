from django.test import Client, TestCase
from django.urls import reverse


class TaskStaticPagesTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_views_use_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = (
            ('about/author.html', reverse('about:author')),
            ('about/tech.html', reverse('about:tech'))
        )
        for template, reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
