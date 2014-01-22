from django.shortcuts import render, redirect, get_object_or_404
from  django.http import HttpResponse
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from css3two_blog.models import BlogPost

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
    args['data'] = [
        ('acg', BlogPost.objects.filter(category="acg")),
        ('programming', BlogPost.objects.filter(category="programming")),
        ('nc', BlogPost.objects.filter(category="nc")),   # no category
    ]
    return render(request, 'css3two_blog/archive.html', args)


def siteinfo(request):
    #return render(request, 'css3two_blog/siteinfo.html', {})
    return HttpResponse("<html>Under development</html>")


def contact(request):
    #return render(request, 'css3two_blog/contact.html', {})
    return HttpResponse("<html>Under development</html>")
