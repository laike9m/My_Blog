import os
import re
from datetime import datetime

from django.db import models
from django.urls import reverse

# delete md_file before delete/change model
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.core.files.base import ContentFile

import markdown2
from taggit.managers import TaggableManager

upload_dir = "content/BlogPost/%s/%s"


_TABLE_TAG_RE = re.compile(r"<(/?)table\b[^>]*>", re.IGNORECASE)


def _wrap_tables(html: str) -> str:
    if "<table" not in html.lower():
        return html

    parts = []
    last_idx = 0
    depth = 0
    wrapped = False
    for match in _TABLE_TAG_RE.finditer(html):
        is_closing = bool(match.group(1))
        if not is_closing:
            if depth == 0:
                prefix = html[last_idx : match.start()]
                parts.append(prefix)
                if not html[: match.start()].rstrip().endswith(
                    '<div class="table-wrapper">'
                ):
                    parts.append('<div class="table-wrapper">')
                    wrapped = True
                else:
                    wrapped = False
                last_idx = match.start()
            depth += 1
        elif depth > 0:
            depth -= 1
            if depth == 0:
                parts.append(html[last_idx : match.end()])
                if wrapped:
                    parts.append("</div>")
                    wrapped = False
                last_idx = match.end()

    parts.append(html[last_idx:])
    if depth > 0 and wrapped:
        parts.append("</div>")
    return "".join(parts)


class BlogPost(models.Model):
    class Meta:
        # ordered by pub_date descending when retriving
        ordering = ["-pub_date"]

    def get_upload_md_name(self, filename):
        if self.pub_date:
            year = self.pub_date.year  # always store in pub_year folder
        else:
            year = datetime.now().year
        upload_to = upload_dir % (year, self.title + ".md")
        return upload_to

    def get_html_name(self, filename):
        if self.pub_date:
            year = self.pub_date.year
        else:
            year = datetime.now().year
        upload_to = upload_dir % (year, filename)
        return upload_to

    CATEGORY_CHOICES = (
        ("programming", "Programming"),
        ("acg", "Anime & Manga & Novel & Game"),
        ("nc", "No Category"),
    )

    title = models.CharField(max_length=150)
    body = models.TextField(blank=True)
    # uploaded md file
    md_file = models.FileField(upload_to=get_upload_md_name, blank=True)
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    last_edit_date = models.DateTimeField("last edited", auto_now=True)
    slug = models.SlugField(max_length=200, blank=False, null=False)
    # generated html file
    html_file = models.FileField(upload_to=get_html_name, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    tags = TaggableManager()

    def __str__(self):
        return (
            self.title
        )  # 根据继承搜索流程,先是实例属性,然后就是类属性,所以这样用没问题

    @property
    def filename(self):
        if self.md_file:
            return os.path.basename(self.title)
        else:
            return "no md_file"

    def save(self, *args, **kwargs):
        if not self.body and self.md_file:
            self.body = self.md_file.read()

        html = markdown2.markdown(
            self.body, extras=["fenced-code-blocks", "tables", "toc", "header-ids"]
        )
        if html.toc_html:
            content_file = ContentFile(
                html.toc_html.encode("utf-8") + html.encode("utf-8")
            )
        else:
            content_file = ContentFile(html.encode("utf-8"))

        self.html_file.save(self.title + ".html", content_file, save=False)
        self.html_file.close()

        super().save(*args, **kwargs)

    def display_html(self):
        with open(self.html_file.path, encoding="utf-8") as f:
            return _wrap_tables(f.read())

    def get_absolute_url(self):
        from . import views

        return reverse(views.blogpost, kwargs={"slug": self.slug, "post_id": self.id})


@receiver(pre_delete, sender=BlogPost)
def blogpost_delete(instance, **kwargs):
    if instance.md_file:
        instance.md_file.delete(save=False)
    if instance.html_file:
        instance.html_file.delete(save=False)
