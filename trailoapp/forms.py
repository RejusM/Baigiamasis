from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Track, Stage

# Forma naudotojo pagrindinės informacijos atnaujinimui
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User  # Naudojamas modelis šiai formai
        fields = ['username', 'first_name', 'last_name', 'email']  # Laukai, įtraukti į formą

# Forma naudotojo profilio informacijos atnaujinimui
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile  # Naudojamas modelis šiai formai
        fields = ['team', 'phone_number', 'address', 'date_of_birth', 'city', 'gender', 'country', 'photo']  # Laukai, įtraukti į formą

# Forma etapo pasirinkimui
class StageForm(forms.Form):
    stage = forms.ModelChoiceField(queryset=Stage.objects.all(), required=True, label="Pasirinkite etapą")  # Išskleidžiamasis sąrašas etapų pasirinkimui

# Forma trasos pasirinkimui pagal pasirinktą etapą
class TrackForm(forms.Form):
    track = forms.ModelChoiceField(queryset=Track.objects.none(), required=True, label="Pasirinkite trasą")  # Išskleidžiamasis sąrašas trasų pasirinkimui

    def __init__(self, stage, *args, **kwargs):
        super(TrackForm, self).__init__(*args, **kwargs)
        # Filtruoti trasas pagal pasirinktą etapą, užtikrinant, kad būtų įtrauktos tik tos trasos, kurios yra susijusios su registracijomis pasirinktame etape
        self.fields['track'].queryset = Track.objects.filter(raceregistration__stage=stage).distinct().order_by('name')
