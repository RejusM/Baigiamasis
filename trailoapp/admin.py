from django.contrib import admin
from .models import Team, UserProfile, Track, Stage, RaceResult, OverallTeamScore, OverallUserScore


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_first_name', 'get_last_name', 'gender', 'team', 'city', 'country')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'team__name', 'city', 'country')
    list_filter = ('team', 'is_captain')

    def get_first_name(self, obj):
        return obj.user.first_name

    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.user.last_name

    get_last_name.short_description = 'Last Name'


class TrackAdmin(admin.ModelAdmin):
    list_display = ('name', 'distance')
    search_fields = ('name',)
    list_filter = ('distance',)


class TrackInline(admin.TabularInline):
    model = Stage.tracks.through
    extra = 1


class StageAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    search_fields = ('name', 'date')
    list_filter = ('date',)
    inlines = [TrackInline]
    ordering = ('date',)


admin.site.register(Team, TeamAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Track, TrackAdmin)
admin.site.register(Stage, StageAdmin)
admin.site.register(RaceResult)
admin.site.register(OverallTeamScore)
admin.site.register(OverallUserScore)
