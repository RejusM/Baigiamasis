from django.contrib import admin
from .models import Team, UserProfile, Track, Stage, RaceResult, OverallTeamScore, OverallUserScore

admin.site.register(Team)
admin.site.register(UserProfile)
admin.site.register(Track)
admin.site.register(Stage)
admin.site.register(RaceResult)
admin.site.register(OverallTeamScore)
admin.site.register(OverallUserScore)

