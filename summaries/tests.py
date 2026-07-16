from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Summary
from .services import SummarizationError, summarize_text


class SummoryTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('alice', password='pass12345')
        self.other = User.objects.create_user('bob', password='pass12345')

    def test_login_required_for_list(self):
        res = self.client.get(reverse('summaries:list'))
        self.assertEqual(res.status_code, 302)

    def test_home_is_create_when_logged_in(self):
        self.client.login(username='alice', password='pass12345')
        res = self.client.get(reverse('summaries:create'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, '原文を貼って')

    def test_cannot_see_others_summary(self):
        Summary.objects.create(
            user=self.other,
            title='secret',
            original_text='orig',
            summary_text='sum',
            category='仕事',
        )
        self.client.login(username='alice', password='pass12345')
        res = self.client.get(reverse('summaries:list'))
        self.assertNotContains(res, 'secret')

    def test_category_filter(self):
        Summary.objects.create(
            user=self.user,
            title='mail',
            original_text='a',
            summary_text='mail summary',
            category='田中さんメール',
        )
        Summary.objects.create(
            user=self.user,
            title='uncategorized-item',
            original_text='b',
            summary_text='no cat',
            category='',
        )
        self.client.login(username='alice', password='pass12345')

        all_res = self.client.get(reverse('summaries:list'))
        self.assertContains(all_res, 'mail')
        self.assertContains(all_res, 'uncategorized-item')

        filtered = self.client.get(
            reverse('summaries:list'),
            {'category': '田中さんメール'},
        )
        self.assertContains(filtered, 'mail')
        self.assertNotContains(filtered, 'uncategorized-item')

    @patch('summaries.views.summarize_text', return_value='・要点A\n・要点B')
    def test_create_summary(self, _mock):
        self.client.login(username='alice', password='pass12345')
        res = self.client.post(reverse('summaries:create'), {
            'title': '',
            'category': '授業資料',
            'original_text': 'これは長い原文です。' * 5,
        })
        self.assertEqual(res.status_code, 302)
        obj = Summary.objects.get(user=self.user)
        self.assertEqual(obj.category, '授業資料')
        self.assertIn('要点A', obj.summary_text)
        self.assertTrue(obj.original_text.startswith('これは長い'))

    def test_delete_own_summary(self):
        obj = Summary.objects.create(
            user=self.user,
            title='t',
            original_text='o',
            summary_text='s',
        )
        self.client.login(username='alice', password='pass12345')
        res = self.client.post(reverse('summaries:delete', args=[obj.pk]))
        self.assertEqual(res.status_code, 302)
        self.assertFalse(Summary.objects.filter(pk=obj.pk).exists())

    def test_cannot_delete_others(self):
        obj = Summary.objects.create(
            user=self.other,
            title='t',
            original_text='o',
            summary_text='s',
        )
        self.client.login(username='alice', password='pass12345')
        res = self.client.post(reverse('summaries:delete', args=[obj.pk]))
        self.assertEqual(res.status_code, 404)

    @override_settings(GEMINI_API_KEY='')
    def test_summarize_without_key(self):
        with self.assertRaises(SummarizationError):
            summarize_text('hello world')
