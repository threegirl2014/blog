from django.contrib import admin
from css3two_blog.models import Blog, BlogImage, Category
from django.contrib.admin.templatetags.admin_list import date_hierarchy
from django import forms
from django.forms.widgets import Textarea, TextInput
from django.contrib.contenttypes.models import ContentType

# Register your models here.

class BlogImageInline(admin.TabularInline):
    model = BlogImage
    extra = 3

class BlogAdminForm(forms.ModelForm):
    class Meta:
        model = Blog
        widgets = {
                   'body' : Textarea(attrs={'cols':100, 'rows':100}),
                   'title' : TextInput(attrs={'size':40}),
                   'description' : Textarea(attrs={'cols':40, 'rows':5}),
                   }
#         fields = ('title', 'slug', 'pub_date', 'body', 'md_file', 'description', 'category', 'tags')
        #equals above sentence
        exclude = ()
        
class BlogAdmin(admin.ModelAdmin):
    form = BlogAdminForm
    inlines = [BlogImageInline,]
    actions = ['make_published','make_draft','make_withdrawn',]
    
    date_hierarchy = 'pub_date'  
    list_display = ('id','title','pub_date','category','status')
    list_filter = ['pub_date','category']
    search_fields = ['title',]
    
    def save_model(self, request, obj, form, change):
        obj.save()
        print obj.slug, "save successfully"

    def make_published(self, request, queryset):
        row_updated = queryset.update(status='p')
        message = "%s blogs was/were successfully marked as published." % row_updated
        self.message_user(request, message)
    make_published.short_description = "Mark selected blogs as published"

    def make_draft(self, request, queryset):
        row_updated = queryset.update(status='d')
        message = "%s blogs was/were successfully marked as draft." % row_updated
        self.message_user(request, message)
    make_draft.short_description = "Mark selected blogs as draft"
    
    def make_withdrawn(self, request, queryset):
        row_updated = queryset.update(status='w')
        message = "%s blogs was/were successfully marked as withdrawn." % row_updated
        self.message_user(request, message)
    make_withdrawn.short_description = "Mark selected blogs as withdrawn"
    
    def export_selected_objects(self, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        ct = ContentType.objects.get_for_model(queryset.model)
        print ct, ",".join(selected)
    export_selected_objects.short_description = "Export selected blogs"
    
admin.site.register(Blog,BlogAdmin)
admin.site.register(BlogImage)
admin.site.register(Category)