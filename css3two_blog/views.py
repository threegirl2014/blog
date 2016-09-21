# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404

from .models import Blog
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from css3two_blog.models import Category
from _collections import defaultdict
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed
from .forms import ContactForm
from django.http.response import HttpResponseRedirect
from django.core.mail import send_mail
from django.conf import settings
# Create your views here.

exclude_blog = ("about","projects")
categorys = Category.objects.all()

def home(request,page='1'):
    raw_blogs = Blog.objects.filter(status='p')
    paginator = Paginator(raw_blogs,5)
    page = int(page)
    try:
        blog_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        blog_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        blog_list = paginator.page(paginator.num_pages)
    return render(request, 'css3two_blog/index.html', {'blog_list' : blog_list, 'categorys' : categorys})
    
def archive(request,name=''):
    
    args = dict()
    args['data'] = []
    blogs = Blog.objects.exclude(title__in=exclude_blog).filter(status='p')
    if name != '':
        categorys_filtered = categorys.filter(short_name=name)
    else:
        categorys_filtered = categorys

    def get_sorted_bloglist(category):
        sorted_by_year = defaultdict(list)
        blog_in_a_category = blogs.filter(category=category)
        for blog in blog_in_a_category:
            year = blog.pub_date.year
            sorted_by_year[year].append(blog)
        #dict.items() returns a list of dict's (key, value) tuple pairs 
        sorted_by_year = sorted(sorted_by_year.items(),reverse=True)
        return sorted_by_year
    
    for category in categorys_filtered:
        bloglist = get_sorted_bloglist(category)
        if len(bloglist) > 0:#to make sure the category have related blogs
            args['data'].append((category,bloglist))
    args['categorys'] = categorys    
    return render(request, 'css3two_blog/archive.html', args)
 
def blog(request,slug,blog_id):
    blog = get_object_or_404(Blog,pk=blog_id)
    return render(request, 'css3two_blog/blog.html',{'blog':blog, 'categorys' : categorys})   

def get_sorted_bloglist(bloglist):
    sorted_by_year = defaultdict(list)
    for blog in bloglist:
        year = blog.pub_date.year
        sorted_by_year[year].append(blog)
    sorted_by_year = sorted(sorted_by_year.items(),reverse=True)
    return sorted_by_year
    
def search_tag(request,name=''):
    if name != '':
        tag = get_object_or_404(Blog.tags,name=name)
        bloglist = Blog.objects.exclude(title__in=exclude_blog).filter(status='p').filter(tags__in=[tag,])
    args = dict()
    args['tag'] = tag
    args['categorys'] = categorys      
    args['bloglist'] = get_sorted_bloglist(bloglist)   
    return render(request, 'css3two_blog/search_tag.html', args)

def search_blog(request):
    args = dict()
    args['categorys'] = categorys
    if 's' in request.GET:
        s = request.GET['s']
        if s:
            bloglist = Blog.objects.exclude(title__in=exclude_blog).filter(status='p').filter(title__icontains=s)
            args['error'] = True if len(bloglist) == 0 else False
            args['s'] = s
            args['bloglist'] = get_sorted_bloglist(bloglist)
            return render(request, 'css3two_blog/search_blog.html',args)
    return render(request, 'css3two_blog/home.html', args)                 

def projects(request):
    pass

def about(request):
    pass

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            sender = form.cleaned_data['email']
            message = form.cleaned_data['message']
#             cc_myself = form.cleaned_data['cc_myself']
            
            recipients = [settings.DEFAULT_FROM_EMAIL,sender]
            send_mail(subject=subject, message=message, recipient_list=recipients,from_email=None)
            return HttpResponseRedirect('/thanks/')
    else:
        form = ContactForm()
    
    return render(request, 'css3two_blog/contact.html', {'form' : form, 'categorys' : categorys}) 

def thanks(request):
    return render(request, 'css3two_blog/thanks.html',{'categorys' : categorys,})

def handler404(request):
    return render(request, 'css3two_blog/404.html', status=404)

class ExtendedRSSFeed(Rss201rev2Feed):
    mime_type = 'application/xml'
    """
    Create a type of RSS feed that has content:encoded elements.
    """
    def root_attributes(self):
        attrs = super(ExtendedRSSFeed, self).root_attributes()
        attrs['xmlns:content'] = 'http://purl.org/rss/1.0/modules/content/'
        return attrs

    def add_item_elements(self, handler, item):
        super(ExtendedRSSFeed, self).add_item_elements(handler, item)
        handler.addQuickElement(u'content:encoded', item['content_encoded'])
        
class RSSFeed(Feed):
    feed_type = ExtendedRSSFeed
    title = "Threegirl2014's Blog"
    link = "/rss/"
    description= "Threegirl2014's Blog Feed."
    
    def items(self):
        return Blog.objects.exclude(title__in=exclude_blog)[:20]
    
    def item_title(self, item):
        return item.title
    
    def item_description(self, item):
        return item.description or '没有简介, 请去看原文吧'
    
    def item_link(self, item):
        return item.get_absolute_url()
    
    def item_pubdate(self,item):
        return item.pub_date
    
    def item_extra_kwargs(self, item):
        return {"content_encoded" : self.item_content_encoded(item)}
    
    def item_content_encoded(self,item):
        return item.body