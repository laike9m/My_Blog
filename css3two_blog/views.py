from django.shortcuts import render, redirect, get_object_or_404
from  django.http import HttpResponse
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from css3two_blog.models import BlogPost
from collections import defaultdict

# Create your views here.
def home(request):
    args = dict()
    args['blogposts'] = BlogPost.objects.all()
    return render(request, 'css3two_blog/index.html', args)


def blogpost(request, slug, id):
    args = {}
    blogpost = get_object_or_404(BlogPost, pk=id)
    args['blogpost'] = blogpost
    return render(request, 'css3two_blog/blogpost.html', args)


def archive(request):
    args = dict()

    def get_sorted_posts(category):
        posts_by_year = defaultdict(list)
        posts_of_a_category = BlogPost.objects.filter(category=category)  # already sorted by pub_date
        for post in posts_of_a_category:
            year = post.pub_date.year
            posts_by_year[year].append(post)  # {'2013':post_list, '2014':post_list}
        posts_by_year = sorted(posts_by_year.items(), reverse=True)  # [('2014',post_list), ('2013',post_list)]
        return posts_by_year

    args['data'] = [
        ('programming', get_sorted_posts(category="programming")),
        ('acg', get_sorted_posts(category="acg")),
        ('nc', get_sorted_posts(category="nc")),   # no category
    ]

    args['MONTH'] = ('JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC')

    from pprint import pprint
    pprint(args['data'])
    return render(request, 'css3two_blog/archive.html', args)


def siteinfo(request):
    #return render(request, 'css3two_blog/siteinfo.html', {})
    return HttpResponse("<html>Under development</html>")


def contact(request):
    #return render(request, 'css3two_blog/contact.html', {})
    return HttpResponse("<html>Under development</html>")
