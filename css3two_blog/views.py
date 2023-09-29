from collections import defaultdict
from math import ceil
from os.path import join

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404

from .models import BlogPost

exclude_posts = ("about", "projects", "talks")


def home(request, page=''):
    args = dict()
    args['blogposts'] = BlogPost.objects.exclude(title__in=exclude_posts)
    max_page = ceil(len(args['blogposts']) / 3)
    if page and int(page) < 2:  # /0, /1 -> /
        return redirect("/")
    else:
        page = int(page) if (page and int(page) > 0) else 1
        args['page'] = page
        args['prev_page'] = page + 1 if page < max_page else None
        args['newer_page'] = page - 1 if page > 1 else None
        # as template slice filter, syntax: list|slice:"start:end"
        args['sl'] = str(3 * (page - 1)) + ':' + str(3 * (page - 1) + 3)
        return render(request, 'css3two_blog/index.html', args)


def blogpost(request, slug, post_id):
    args = {'blogpost': get_object_or_404(BlogPost, pk=post_id)}
    return render(request, 'css3two_blog/blogpost.html', args)


def archive(request):
    posts_by_year = defaultdict(list)
    blogposts = BlogPost.objects.exclude(title__in=exclude_posts)

    for post in blogposts:
        year = post.pub_date.year
        posts_by_year[year].append(post)  # {'2013':post_list, '2014':post_list}
    posts_by_year = sorted(posts_by_year.items(), reverse=True)  # [('2014',post_list), ('2013',post_list)]

    return render(request, 'css3two_blog/archive.html', {'posts_by_year': posts_by_year})


def about(request):
    the_about_post = get_object_or_404(BlogPost, title="about")
    args = {"about": the_about_post}
    return render(request, 'css3two_blog/about.html', args)


def projects(request):
    # use markdown to show projects
    the_projects_post = get_object_or_404(BlogPost, title="projects")
    args = {"projects": the_projects_post}
    return render(request, 'css3two_blog/projects.html', args)


def talks(request):
    # use markdown to show talks, could be changed if need better formatting
    the_talks_post = get_object_or_404(BlogPost, title="talks")
    args = {"talks": the_talks_post}
    return render(request, 'css3two_blog/talks.html', args)


def contact(request):
    html = "<meta http-equiv=\"refresh\" content=\"3;url=" \
           "/\">Under Development. Will return to homepage."
    return HttpResponse(html)


def article(request, freshness):
    """ redirect to article accroding to freshness, latest->oldest:freshness=1->N """
    if freshness.isdigit():
        try:
            article_url = BlogPost.objects.all()[int(freshness) - 1].get_absolute_url()
            return redirect(article_url)
        except IndexError:
            raise Http404
        except AssertionError:  # freshness=0
            raise Http404
    else:
        return redirect('/')
