from django.contrib import admin

from .models import Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "text",
        "pub_date",
        "author",
        "group",
    )
    date_hierarchy = "pub_date"
    list_editable = ("group",)
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "title",
        "slug",
        "description",
    )
    search_fields = ("title", "description")
    empty_value_display = "-пусто-"


# Надо исправить: Обе модели регистрируем в админке
admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
