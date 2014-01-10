import os

from django.db import models
from django.utils import timezone

# for slug, get_absolute_url
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from unidecode import unidecode

# delete md_file before delete/change model
from django.db.models.signals import pre_delete
from django.dispatch import receiver

# get gfm html and store it
import requests
from django.core.files.base import ContentFile


upload_dir = 'content/BlogPost/%s/%s'


class BlogPost(models.Model):

    def get_upload_md_name(self, filename):
        year = self.pub_date.year   # always store in pub_year folder
        upload_to = upload_dir % (year, self.title + '.md')
        return upload_to

    def get_html_name(self, filename):
        year = self.pub_date.year
        upload_to = upload_dir % (year, filename)
        return upload_to

    title = models.CharField(max_length=150)
    body = models.TextField(blank=True)
    md_file = models.FileField(upload_to=get_upload_md_name, blank=True)  # uploaded md file
    pub_date = models.DateTimeField('date published', default=timezone.now())
    last_edit_date = models.DateTimeField('last edited', default=timezone.now())
    slug = models.SlugField(blank=True)
    html_file = models.FileField(upload_to=get_html_name, blank=True)    # generated html file

    def __str__(self):
        return self.title   # 根据继承搜索流程,先是实例属性,然后就是类属性,所以这样用没问题

    @property
    def filename(self):
        if self.md_file:
            return os.path.basename(self.md_file.name)
        else:
            return 'no md_file'

    def save(self, *args, **kwargs):
        self.slug = slugify(unidecode(self.title))
        if not self.body and self.md_file:
            self.body = self.md_file.read()   # self.body store bytes rather than string !

        # generate rendered html file with same name as md
        data = str(self.body)[2:-1].encode('utf-8').decode('unicode_escape')
        headers = {'Content-Type': 'text/plain'}
        r = requests.post('https://api.github.com/markdown/raw', headers=headers, data=data)
        self.html_file.save(self.title+'.html', ContentFile(r.text), save=False)  # avoid recursive invoke
        self.html_file.close()

        super().save(*args, **kwargs)

    def display_html(self):
        fp = open(self.html_file.path)
        t = fp.read().replace('\n', '')  # 如果不去掉\n就会有多余的<br>, 原因未知
        return t

    def get_absolute_url(self):
        return reverse('css3two_blog.views.blogpost', kwargs={'slug': self.slug, 'id': self.id})


@receiver(pre_delete, sender=BlogPost)
def blogpost_delete(instance, **kwargs):
    if instance.md_file:
        instance.md_file.delete(save=False)
    if instance.html_file:
        instance.html_file.delete(save=False)

