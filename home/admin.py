from django.contrib import admin

from .models import ContactMessage, Feedback, Profile, Show


@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "genre",
        "release_year",
        "maturity_rating",
        "match_score",
        "trending",
        "featured",
        "top10_rank",
    )
    list_filter = ("genre", "maturity_rating", "trending", "featured")
    search_fields = ("title", "description", "cast", "creator")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-added_on",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "country", "gender", "newsletter_opt_in", "created_on")
    search_fields = ("user__username", "user__email", "country")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_on", "resolved")
    list_filter = ("resolved",)
    search_fields = ("name", "email", "subject", "message")


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "feedback_type", "rating", "created_on")
    list_filter = ("feedback_type", "rating")
    search_fields = ("full_name", "email", "message")
