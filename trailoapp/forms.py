from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, RaceResult, Track, Stage


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['team', 'phone_number', 'address', 'date_of_birth', 'city', 'gender', 'country', 'photo']


class StageForm(forms.Form):
    stage = forms.ModelChoiceField(queryset=Stage.objects.all(), required=True, label="Pasirinkite etapą")


class TrackForm(forms.Form):
    track = forms.ModelChoiceField(queryset=Track.objects.none(), required=True, label="Pasirinkite trasą")

    def __init__(self, stage, *args, **kwargs):
        super(TrackForm, self).__init__(*args, **kwargs)
        self.fields['track'].queryset = Track.objects.filter(raceregistration__stage=stage).distinct().order_by('name')
