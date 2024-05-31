from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, RaceResult, OverallUserScore, OverallTeamScore
from django.db.models import Sum


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


@receiver(post_save, sender=RaceResult)
@receiver(post_delete, sender=RaceResult)
def update_overall_scores(sender, instance, **kwargs):
    user_profile = instance.user_profile
    user_score, created = OverallUserScore.objects.get_or_create(user_profile=user_profile)
    user_score.total_points = RaceResult.objects.filter(user_profile=user_profile).aggregate(Sum('points'))[
                                  'points__sum'] or 0
    user_score.save()

    if user_profile.team:
        team = user_profile.team
        team_score, created = OverallTeamScore.objects.get_or_create(team=team)
        team_score.total_points = RaceResult.objects.filter(user_profile__team=team).aggregate(Sum('points'))[
                                      'points__sum'] or 0
        team_score.save()
