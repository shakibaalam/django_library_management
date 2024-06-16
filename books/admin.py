from django.contrib import admin
from . import models

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('name',)}
    list_display = ['name', 'slug']
    
admin.site.register(models.BookModel)
admin.site.register(models.CategoryModel,CategoryAdmin)
admin.site.register(models.ReviewModel)
