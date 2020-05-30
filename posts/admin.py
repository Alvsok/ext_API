from django.contrib import admin
from .models import Post, Group, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author", "group")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class PostGroup(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "description")
    search_fields = ("title",)
    empty_value_display = "-пусто-"

class PostComment(admin.ModelAdmin):
    list_display = ("pk", "post", "author", "text", "created")
    search_fields = ("title",)
    empty_value_display = "-пусто-"
    

admin.site.register(Post, PostAdmin)
admin.site.register(Group, PostGroup)
admin.site.register(Comment, PostComment)

