from django.contrib import admin
from .models import DanceClub, Dancer

class DancerInline(admin.TabularInline):
    model = Dancer
    extra = 0  # don't show extra blank fields

@admin.register(DanceClub)
class DanceClubAdmin(admin.ModelAdmin):
    list_display = ('club_name', 'user', 'country', 'city', 'phone_number', 'representative_name')
    inlines = [DancerInline]

@admin.register(Dancer)
class DancerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'date_of_birth', 'club')
