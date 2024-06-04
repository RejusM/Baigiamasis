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


class RaceResultForm(forms.ModelForm):
    stage = forms.ModelChoiceField(queryset=Stage.objects.all(), label='Varžybos', required=True)
    user = forms.ModelChoiceField(queryset=UserProfile.objects.all(), label='Vartotojas', required=True)
    track = forms.ModelChoiceField(queryset=Track.objects.all(), label='Trasa', required=True)

    class Meta:
        model = RaceResult
        fields = ['stage', 'user', 'track', 'points', 'position']

    def __init__(self, *args, **kwargs):
        super(RaceResultForm, self).__init__(*args, **kwargs)
        if 'stage_id' in self.data:
            try:
                stage_id = int(self.data.get('stage_id'))
                self.fields['track'].queryset = Track.objects.filter(stages__id=stage_id)
            except (ValueError, TypeError):
                self.fields['track'].queryset = Track.objects.none()
        elif self.instance.pk:
            self.fields['track'].queryset = self.instance.stage.tracks.all()


class StageForm(forms.Form):
    stage = forms.ModelChoiceField(queryset=Stage.objects.all(), required=True, label="Pasirinkite etapą")


class TrackForm(forms.Form):
    track = forms.ModelChoiceField(queryset=Track.objects.none(), required=True, label="Pasirinkite trasą")

    def __init__(self, stage, *args, **kwargs):
        super(TrackForm, self).__init__(*args, **kwargs)
        self.fields['track'].queryset = Track.objects.filter(raceregistration__stage=stage).distinct().order_by('name')
