# admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import ChatSession, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 1
    fields = ["role", "text", "file_uri", "is_image", "reply_to", "date_created"]
    readonly_fields = ["date_created"]

    # Pre-set role to MODEL for new inline entries so admin replies correctly
    def get_extra(self, request, obj=None, **kwargs):
        return 1

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields["role"].initial = Message.Role.MODEL
        return formset


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "title", "message_count", "date_updated"]
    list_filter = ["date_updated"]
    search_fields = ["user__email", "title"]
    inlines = [MessageInline]
    readonly_fields = ["date_created", "date_updated"]

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = "Messages"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["id", "session", "role", "short_text", "has_file", "date_created"]
    list_filter = ["role", "date_created"]
    search_fields = ["text", "session__user__email"]
    readonly_fields = ["date_created"]
    list_select_related = ["session__user"]

    # ── Quick-reply action from the message list ──────────────────────────
    actions = ["reply_to_selected"]

    def short_text(self, obj):
        return obj.text[:60] if obj.text else "—"
    short_text.short_description = "Text"

    def has_file(self, obj):
        return bool(obj.file_uri)
    has_file.boolean = True
    has_file.short_description = "File"