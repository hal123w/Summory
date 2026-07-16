from django.contrib import admin

from .models import Summary


@admin.register(Summary)
class SummaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'user', 'created_at')
    list_filter = ('category',)
    search_fields = ('title', 'summary_text', 'original_text', 'user__username')
