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
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL)
    is_captain = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    date_of_birth = models.CharField(max_length=4, help_text='Įveskite gimimo metus',)
    city = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=[('V', 'Vyras'), ('M', 'Moteris')])
    country = models.CharField(max_length=100, blank=True, null=True)
    photo = models.ImageField(upload_to='profile_photos/', default='default-user.png')

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
    registration_start = models.DateTimeField()
    registration_end = models.DateTimeField()
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
        verbose_name = 'Bendri komandų rezultatai'
        verbose_name_plural = 'Bendri komandų rezultatai'


class OverallUserScore(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    total_points = models.FloatField(default=0)

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.total_points} points"

    class Meta:
        verbose_name = 'Bendri dalyvių rezultatai'
        verbose_name_plural = 'Bendri dalyvių rezultatai'


class RaceRegistration(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True, null=True)
    STATUS_CHOICES = [
        ('n', 'Neperžiūrėta'),
        ('p', 'Patvirtinta'),
        ('a', 'Atmesta'),
    ]
    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        blank=True,
        default='n',
        help_text='Registracijos statusas',
    )

    class Meta:
        unique_together = ('user_profile', 'stage')
        verbose_name = 'Varžybų registracija'
        verbose_name_plural = 'Varžybų registracijos'

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.stage.name} registracija"
