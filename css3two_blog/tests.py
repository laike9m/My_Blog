import json
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from css3two_blog.summarizer import (
    DEFAULT_SUMMARY_MODEL,
    SYSTEM_PROMPT_EN,
    SYSTEM_PROMPT_ZH,
    summarize_post,
)


class BlogPostAdminTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.superuser = User.objects.create_superuser(
            username="admin_tester",
            email="admin@example.com",
            password="password123",
        )
        self.staff_without_perms = User.objects.create_user(
            username="staff_no_perm",
            email="staff@example.com",
            password="password123",
            is_staff=True,
        )
        self.summarize_url = reverse("admin:css3two_blog_blogpost_summarize")

    def test_add_page_renders_resized_body_and_summarize_button(self):
        self.client.force_login(self.superuser)
        response = self.client.get(reverse("admin:css3two_blog_blogpost_add"))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf-8")

        self.assertIn('rows="25"', html)
        self.assertIn('cols="140"', html)
        self.assertIn("css3two_blog/css/blogpost_admin.css", html)
        self.assertIn("css3two_blog/js/blogpost_admin.js", html)
        self.assertIn('id="summarize-description-btn"', html)
        self.assertIn(f'data-summarize-url="{self.summarize_url}"', html)

    def test_summarize_requires_admin_login(self):
        response = self.client.post(
            self.summarize_url,
            data=json.dumps({"title": "Test", "body": "Content"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 302)

    def test_summarize_requires_model_permission(self):
        self.client.force_login(self.staff_without_perms)
        response = self.client.post(
            self.summarize_url,
            data=json.dumps({"title": "Test", "body": "Content"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_summarize_rejects_get_and_empty_body(self):
        self.client.force_login(self.superuser)

        get_resp = self.client.get(self.summarize_url)
        self.assertEqual(get_resp.status_code, 405)

        empty_resp = self.client.post(
            self.summarize_url,
            data=json.dumps({"title": "Hello", "body": "   "}),
            content_type="application/json",
        )
        self.assertEqual(empty_resp.status_code, 400)
        self.assertIn("empty", empty_resp.json()["error"].lower())

    @patch("css3two_blog.admin.summarize_post", return_value="这是一段文章总结。")
    def test_summarize_endpoint_success(self, mock_summarize):
        self.client.force_login(self.superuser)
        response = self.client.post(
            self.summarize_url,
            data=json.dumps({"title": "测试标题", "body": "文章正文内容"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"summary": "这是一段文章总结。"})
        mock_summarize.assert_called_once_with(body="文章正文内容", title="测试标题")


class SummarizerTests(TestCase):
    @patch.dict("os.environ", {"DEEPSEEK_API_KEY": "sk-test-key"}, clear=False)
    @patch("css3two_blog.summarizer.litellm.completion")
    def test_summarize_post_calls_litellm_deepseek_flash(self, mock_completion):
        mock_completion.return_value = SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="  A concise summary.  ")
                )
            ]
        )

        result = summarize_post(body="Full markdown article.", title="My Post")
        self.assertEqual(result, "A concise summary.")

        mock_completion.assert_called_once()
        kwargs = mock_completion.call_args.kwargs
        self.assertEqual(kwargs["model"], DEFAULT_SUMMARY_MODEL)
        self.assertEqual(kwargs["model"], "deepseek/deepseek-flash")
        self.assertEqual(kwargs["reasoning_effort"], "none")
        self.assertTrue(kwargs["drop_params"])
        self.assertEqual(len(kwargs["messages"]), 2)
        self.assertEqual(kwargs["messages"][0]["content"], SYSTEM_PROMPT_EN)
        self.assertIn("My Post", kwargs["messages"][1]["content"])
        self.assertIn("Full markdown article.", kwargs["messages"][1]["content"])

    @patch.dict("os.environ", {"DEEPSEEK_API_KEY": "sk-test-key"}, clear=False)
    @patch("css3two_blog.summarizer.litellm.completion")
    def test_summarize_post_uses_chinese_prompt_for_chinese_body(self, mock_completion):
        mock_completion.return_value = SimpleNamespace(
            choices=[
                SimpleNamespace(message=SimpleNamespace(content="这是一段中文简介。"))
            ]
        )

        result = summarize_post(
            body="这是一篇讨论 Python GIL 和并发性能的中文技术文章。",
            title="Why Is GIL Worse Than We Thought?",
        )
        self.assertEqual(result, "这是一段中文简介。")
        kwargs = mock_completion.call_args.kwargs
        self.assertEqual(kwargs["messages"][0]["content"], SYSTEM_PROMPT_ZH)

    @patch.dict("os.environ", {"DEEPSEEK_API_KEY": ""}, clear=False)
    def test_summarize_post_missing_api_key(self):
        with self.assertRaises(ValueError):
            summarize_post(body="Some content")

