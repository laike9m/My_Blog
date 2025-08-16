# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers
import css3two_blog.models


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('title', models.CharField(max_length=150)),
                ('body', models.TextField(blank=True)),
                ('md_file', models.FileField(blank=True, upload_to=css3two_blog.models.BlogPost.get_upload_md_name)),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='date published')),
                ('last_edit_date', models.DateTimeField(verbose_name='last edited', auto_now=True)),
                ('slug', models.SlugField(blank=True, max_length=200)),
                ('html_file', models.FileField(blank=True, upload_to=css3two_blog.models.BlogPost.get_html_name)),
                ('category', models.CharField(max_length=30, choices=[('programming', 'Programming'), ('acg', 'Anime & Manga & Novel & Game'), ('nc', 'No Category')])),
                ('tags', taggit.managers.TaggableManager(through='taggit.TaggedItem', verbose_name='Tags', help_text='A comma-separated list of tags.', to='taggit.Tag')),
            ],
            options={
                'ordering': ['-pub_date'],
            },
        ),
    ]
