from django.contrib import admin
from .models import OnboardingForm, GeneratedMaterial, GoogleAccountMap, RecordingJob

admin.site.register(OnboardingForm)
admin.site.register(GeneratedMaterial)


@admin.register(GoogleAccountMap)
class GoogleAccountMapAdmin(admin.ModelAdmin):
    list_display = ('pipedrive_user_id', 'google_email', 'name')
    search_fields = ('pipedrive_user_id', 'google_email', 'name')


@admin.register(RecordingJob)
class RecordingJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'deal_id', 'meet_code', 'owner_google_email', 'status', 'attempts', 'created_at')
    list_filter = ('status',)
    search_fields = ('deal_id', 'activity_id', 'meet_code', 'owner_google_email')
    readonly_fields = ('created_at', 'updated_at')
