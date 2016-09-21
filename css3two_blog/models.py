# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from taggit.managers import TaggableManager
from django.template.defaultfilters import slugify
from unidecode import unidecode
from taggit.models import TaggedItem
from django.utils import timezone
from django.core.urlresolvers import reverse
from datetime import datetime
from django.core.files.base import ContentFile
# when create mysql database should use this command for Chinese words:
# create database database_name default character set utf8 collate utf8_general_ci;
# the inspect command:
# show create database database_name;
# show create table table_name;

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50)
    short_name = models.CharField(max_length=10)
    
    def __unicode__(self):
        return self.short_name

mdfile_upload_dir = 'Content/Blogs/%s/%s'
image_upload_dir = 'Content/Images/%s/%s'

def get_upload_md_name(obj,filename):
    if obj.pub_date:
        year = obj.pub_date.year
    else:
        year = datetime.now().year
    upload_to = mdfile_upload_dir % (year, obj.slug + '.markdown')
    return upload_to

class Blog(models.Model):
    
    class Meta:
        ordering = ['-pub_date']
    
    STATUS_CHOICES = (
                      ('d', 'Draft'),
                      ('p', 'Published'),
                      ('w', 'Withdrawn'),
                      )                   
                     
    
    title = models.CharField('title',max_length=100)
    slug = models.SlugField(max_length=200,blank=True)
    
#     pub_date = models.DateTimeField('date published', auto_now_add=True)
    #if set auto_now=True or auto_now_add=True, the time variable is read-only.
    #default=timezone.now(), can auto set the time and also give the choice to change it
    #to support this function, we should set USE_TZ=False
    pub_date = models.DateTimeField('date published', default=timezone.now())
    last_edit_date = models.DateTimeField('last edited', auto_now=True)
    
    body = models.TextField(blank=True)
    md_file = models.FileField(upload_to=get_upload_md_name,blank=True)
    description = models.TextField(blank=True)
    
    category = models.ForeignKey(Category)
    tags = TaggableManager()
    
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='d')
    
    def __unicode__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.slug = slugify(unidecode(self.title))
        if not self.body and self.md_file:#create blog by md file
            self.body = self.md_file.read()
        else:#create blog by body OR when modify blog
            if self.md_file:#delete first if the file exists
                self.md_file.delete(save=False)
            self.md_file.save(self.slug + '.markdown', ContentFile(self.body.encode('utf-8')), save=False)
            
        print self.title,type(self.title),type(self.body)
                       
        super(Blog,self).save(*args,**kwargs)
        
    def get_absolute_url(self):
        return reverse('blog', kwargs={'slug':self.slug,'blog_id':self.id})

def get_upload_image_name(obj,filename):
    if obj.blog.pub_date:
        year = obj.blog.pub_date.year
    else:
        year = datetime.now().year
    upload_to = image_upload_dir % (year, filename)
    return upload_to
 
class BlogImage(models.Model):
    blog = models.ForeignKey(Blog,related_name='images')
    image = models.FileField(upload_to=get_upload_image_name)   