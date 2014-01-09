from datetime import date
import os

from django.db import models
from django.utils import timezone

# for slug, get_absolute_url
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from unidecode import unidecode

# delete md_file before delete model
from django.db.models.signals import pre_delete
from django.dispatch import receiver

# get gfm html and store it
from django.conf import settings
from os.path import join
import requests


upload_dir = 'content/BlogPost/%s/%s'


def get_upload_file_name(instance, filename):
    year = date.today().year    # 按照年份存放
    upload_to = upload_dir % (year, instance.title + '.md')
    return upload_to


class BlogPost(models.Model):

    title = models.CharField(max_length=150)
    body = models.TextField(blank=True)
    md_file = models.FileField(upload_to=get_upload_file_name, blank=True)  # 上传md文件
    pub_date = models.DateTimeField('date published', default=timezone.now())
    last_edit_date = models.DateTimeField('last edited', default=timezone.now())
    slug = models.SlugField(blank=True)
    
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
            self.body = self.md_file.read()   # bytes !

        # generate rendered html file with same name as md
        #if exists 同名html文件 delete
        data = str(self.body)[2:-1].encode('utf-8').decode('unicode_escape')
        headers = {'Content-Type': 'text/plain'}
        r = requests.post('https://api.github.com/markdown/raw', headers=headers, data=data)
        media_root = settings.MEDIA_ROOT
        year = date.today().year
        self.html_filename = join(media_root, upload_dir % (year, self.title + '.html'))
        with open(self.html_filename, 'wt') as f:
            print(r.text)
            f.write(r.text)

        super(BlogPost, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('css3two_blog.views.blogpost', kwargs={'slug': self.slug, 'id': self.id})


@receiver(pre_delete, sender=BlogPost)
def blogpost_delete(instance, **kwargs):
    if instance.md_file:
        instance.md_file.delete()
    if os.path.exists(instance.html_filename):
        os.remove(instance.html_filename)

