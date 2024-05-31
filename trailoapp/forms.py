from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, RaceResult, RaceRegistration, Track


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['team', 'phone_number', 'address', 'date_of_birth', 'city', 'gender', 'country', 'photo']


class RaceResultForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=UserProfile.objects.none(), label="Vartotojas")

    class Meta:
        model = RaceResult
        fields = ['user', 'stage', 'track', 'points', 'position']

    def __init__(self, *args, **kwargs):
        stage_id = kwargs.pop('stage_id', None)
        super().__init__(*args, **kwargs)
        if stage_id:
            self.fields['user'].queryset = UserProfile.objects.filter(
                id__in=RaceRegistration.objects.filter(stage_id=stage_id).values_list('user_profile_id', flat=True)
            )
            self.fields['user'].label_from_instance = lambda obj: f"{obj.user.first_name} {obj.user.last_name}"
            self.fields['track'].queryset = Track.objects.filter(stages__id=stage_id)
