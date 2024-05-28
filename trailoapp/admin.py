from django.contrib import admin
from .models import Team, UserProfile, Track, Stage, RaceResult, OverallTeamScore, OverallUserScore


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'team', 'city', 'country')
    search_fields = ('team_name', 'city', 'country')
    list_filter = ('team', 'is_captain')


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
