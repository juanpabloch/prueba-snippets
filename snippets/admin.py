from django.contrib import admin

from .models import Language, User, Snippet


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
    )



admin.site.register(User)
admin.site.register(Snippet)