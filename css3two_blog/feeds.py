from .models import BlogPost
from django.contrib.syndication.views import Feed

exclude_posts = ("about", "projects")


class BlogPostFeed(Feed):
    title = "latest articles"
    link = "/blog/rss"
    description = "Update on laike9m blog's articles."

    def items(self):
        return BlogPost.objects.exclude(title__in=exclude_posts)

    def item_title(self, item):
        return item.title

    def item_link(self, item):
        return item.get_absolute_url()

    def item_description(self, item):
        return item.display_html()

    def item_pubdate(self, item):
        return item.pub_date
