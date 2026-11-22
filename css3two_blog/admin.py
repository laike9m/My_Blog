import json
import logging
import platform

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AdminTextareaWidget
from django.core.files.base import ContentFile
from django.forms import TextInput, Textarea
from django.http import JsonResponse
from django.urls import path, reverse
from django.utils.html import format_html

from .models import BlogPost
from .summarizer import summarize_post

logger = logging.getLogger(__name__)


class DescriptionSummarizeWidget(AdminTextareaWidget):
    def render(self, name, value, attrs=None, renderer=None):
        textarea_html = super().render(name, value, attrs=attrs, renderer=renderer)
        summarize_url = reverse("admin:css3two_blog_blogpost_summarize")
        return format_html(
            '<div class="description-field-wrapper">'
            "{}"
            '<div class="description-summarize-bar">'
            '<button type="button" id="summarize-description-btn" class="button" data-summarize-url="{}">'
            "AI Summarize"
            "</button>"
            '<span id="summarize-description-status" class="summarize-status" role="status" aria-live="polite"></span>'
            "</div>"
            "</div>",
            textarea_html,
            summarize_url,
        )


class BlogPostAdminForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        widgets = {
            "body": Textarea(attrs={"rows": 25, "cols": 140}),
            "title": TextInput(attrs={"size": 40}),
            "description": DescriptionSummarizeWidget(attrs={"rows": 5}),
        }
        exclude = ("html_file",)

    class Media:
        css = {
            "all": ("css3two_blog/css/blogpost_admin.css",),
        }
        js = ("css3two_blog/js/blogpost_admin.js",)


class BlogPostAdmin(admin.ModelAdmin):
    form = BlogPostAdminForm

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "summarize/",
                self.admin_site.admin_view(self.summarize_view),
                name="css3two_blog_blogpost_summarize",
            ),
        ]
        return custom_urls + urls

    def summarize_view(self, request):
        if request.method != "POST":
            return JsonResponse({"error": "POST method required."}, status=405)

        if not (
            self.has_add_permission(request) or self.has_change_permission(request)
        ):
            return JsonResponse({"error": "Permission denied."}, status=403)

        try:
            payload = json.loads(request.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return JsonResponse({"error": "Invalid JSON payload."}, status=400)

        if not isinstance(payload, dict):
            return JsonResponse({"error": "JSON object required."}, status=400)

        body = payload.get("body", "")
        title = payload.get("title", "")
        if not isinstance(body, str) or not body.strip():
            return JsonResponse({"error": "Article body is empty."}, status=400)
        if not isinstance(title, str):
            title = ""

        try:
            summary = summarize_post(body=body, title=title)
        except ValueError as exc:
            return JsonResponse({"error": str(exc)}, status=400)
        except Exception as exc:
            logger.exception("Failed to summarize blog post")
            return JsonResponse(
                {"error": f"Failed to generate summary: {exc}"}, status=502
            )

        return JsonResponse({"summary": summary})

    def save_model(self, request, obj, form, change):
        if obj:
            if obj.body:  # body有内容的时候才会更新md_file
                filename = obj.filename
                if filename != "no md_file":
                    # On Windows file can't be removed so leave it
                    if platform.system() == "Windows":
                        pass
                    else:
                        obj.md_file.delete(
                            save=False
                        )  # 部署的时候存在,可以正常删除文件
                        obj.html_file.delete(save=False)
                # 没有md_file就根据title创建一个, 但不能创建html因为obj.save()的时候会创建
                obj.md_file.save(filename + ".md", ContentFile(obj.body), save=False)
                obj.md_file.close()
        obj.save()


admin.site.register(BlogPost, BlogPostAdmin)
