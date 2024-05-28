from django.db import models
from django.contrib.auth.models import User


class Team(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Komanda'
        verbose_name_plural = 'Komandos'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    is_captain = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.IntegerField(help_text='Įveskite gimimo metus')
    city = models.CharField(max_length=100, )
    gender = models.CharField(max_length=10, choices=[('V', 'Vyras'), ('M', 'Moteris')])
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Profilis'
        verbose_name_plural = 'Profiliai'


class Track(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    distance = models.FloatField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name}- {self.distance}"

    class Meta:
        verbose_name = 'Trasa'
        verbose_name_plural = 'Trasos'


class Stage(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    photo_link = models.URLField(blank=True, null=True)
    tracks = models.ManyToManyField(Track, related_name='stages')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Etapas'
        verbose_name_plural = 'Etapai'


class RaceResult(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    points = models.FloatField()
    position = models.IntegerField()

    class Meta:
        unique_together = ('user_profile', 'stage', 'track')
        verbose_name = 'Rezultatai'
        verbose_name_plural = 'Rezultatai'

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.stage.name}: {self.points} points, Position: {self.position}"


class OverallTeamScore(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    total_points = models.FloatField(default=0)

    def __str__(self):
        return f"{self.team.name} - {self.total_points} points"

    class Meta:
        verbose_name = 'Bnedri komandų rezultatai'
        verbose_name_plural = 'Bnedri komandų rezultatai'


class OverallUserScore(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    total_points = models.FloatField(default=0)

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.total_points} points"

    class Meta:
        verbose_name = 'Bnedri dalyvių rezultatai'
        verbose_name_plural = 'Bnedri dalyvių rezultatai'