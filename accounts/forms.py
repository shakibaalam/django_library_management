from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserAccountModel, UserAddressModel

GENDER_TYPE = (
    ('Male', 'Male'),
    ('Female', 'Female'),
)

class UserRegistrationForm(UserCreationForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'birth_date', 'gender', 'postal_code', 'city', 'country', 'street_address']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            UserAddressModel.objects.create(
                user=user,
                postal_code=self.cleaned_data['postal_code'],
                country=self.cleaned_data['country'],
                city=self.cleaned_data['city'],
                street_address=self.cleaned_data['street_address']
            )
            UserAccountModel.objects.create(
                user=user,
                gender=self.cleaned_data['gender'],
                birth_date=self.cleaned_data['birth_date'],
                account_no=100000 + user.id
            )
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })


class UserUpdateForm(forms.ModelForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': (
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-700 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })
        if self.instance:
            try:
                user_account = self.instance.account
                user_address = self.instance.address
            except UserAccountModel.DoesNotExist:
                user_account = None
                user_address = None

            if user_account:
                self.fields['gender'].initial = user_account.gender
                self.fields['birth_date'].initial = user_account.birth_date
            if user_address:
                self.fields['street_address'].initial = user_address.street_address
                self.fields['city'].initial = user_address.city
                self.fields['postal_code'].initial = user_address.postal_code
                self.fields['country'].initial = user_address.country

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

            user_account, created = UserAccountModel.objects.update_or_create(
                user=user,
                defaults={
                    'gender': self.cleaned_data['gender'],
                    'birth_date': self.cleaned_data['birth_date'],
                    'account_no': self.generate_account_no(user),
                }
            )

            user_address, created = UserAddressModel.objects.update_or_create(
                user=user,
                defaults={
                    'street_address': self.cleaned_data['street_address'],
                    'city': self.cleaned_data['city'],
                    'postal_code': self.cleaned_data['postal_code'],
                    'country': self.cleaned_data['country'],
                }
            )

        return user

    def generate_account_no(self, user):
        if hasattr(user, 'account') and user.account and user.account.account_no:
            return user.account.account_no
        return 100000 + user.id

