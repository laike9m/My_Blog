from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from .models import BlogPost
from collections import defaultdict
from math import ceil


# Create your views here.
def home(request, page=''):
    args = dict()
    args['blogposts'] = BlogPost.objects.exclude(title="about")
    max_page = ceil(len(args['blogposts'])/3)
    if page and int(page) < 2:  # /0, /1 -> /
        return redirect("/")
    else:
        page = int(page) if (page and int(page) > 0) else 1
        args['page'] = page
        args['prev_page'] = page + 1 if page < max_page else None
        args['newer_page'] = page - 1 if page > 1 else None
        # as template slice filter, syntax: list|slice:"start:end"
        args['sl'] = str(3*(page-1)) + ':' + str(3*(page-1)+3)
        return render(request, 'css3two_blog/index.html', args)


def blogpost(request, slug, id):
    blogpost = get_object_or_404(BlogPost, pk=id)
    args = {'blogpost': blogpost}
    return render(request, 'css3two_blog/blogpost.html', args)


def archive(request):
    args = dict()
    blogposts = BlogPost.objects.exclude(title="about")

    def get_sorted_posts(category):
        posts_by_year = defaultdict(list)
        posts_of_a_category = blogposts.filter(category=category)  # already sorted by pub_date
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

    return render(request, 'css3two_blog/archive.html', args)


def about(request):
    #return render(request, 'css3two_blog/siteinfo.html', {})
    the_about_post = get_object_or_404(BlogPost, title="about")
    args = {"about": the_about_post}
    return render(request, 'css3two_blog/about.html', args)


def contact(request):
    #return render(request, 'css3two_blog/contact.html', {})
    html = "<meta http-equiv=\"refresh\" content=\"3;url=/\">Under Development. Will return to homepage."
    return HttpResponse(html)
