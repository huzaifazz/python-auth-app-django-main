from django.contrib import admin
from .models import BlacklistedToken

# Register your models here.

@admin.register(BlacklistedToken)
class BlacklistedTokenAdmin(admin.ModelAdmin):
    list_display = ['id', 'blacklisted_at']
    search_fields = ['token']
