from django import forms
from mainApp.models import UserProfile
from django.contrib.auth.models import User


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=20,
                               label='Username')
    first_name = forms.CharField(max_length=20,
                                 label='First name')
    last_name = forms.CharField(max_length=20,
                                label='Last name')
    password_1 = forms.CharField(max_length=50,
                                 label='Password',
                                 widget=forms.PasswordInput())
    password_2 = forms.CharField(max_length=50,
                                 label='Confirm password',
                                 widget=forms.PasswordInput())

    class Meta:
        model = UserProfile
        exclude = ('user', 'password', 'gmail_id', 'friends', 'contacts', 'threads', 'picture', 'bio')

    # Customizes form validation for properties that apply to more
    # than one field.  Overrides the forms.Form.clean function.
    def clean(self):
        # Calls our parent (forms.Form) .clean function, gets a dictionary
        # of cleaned data as a result
        cleaned_data = super(RegistrationForm, self).clean()

        # Confirms that the two password fields match
        password_1 = cleaned_data.get('password_1')
        password_2 = cleaned_data.get('password_2')
        if password_1 and password_2 and password_1 != password_2:
            raise forms.ValidationError("Passwords did not match.")

        # Generally return the cleaned data we got from our parent.
        return cleaned_data

    # Customizes form validation for the username field.
    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if not username:
            raise forms.ValidationError("Username must have at least one character.")
        else:
            if User.objects.filter(username__exact=username):
                raise forms.ValidationError("Username is already taken.")

        # Generally return the cleaned data we got from the cleaned_data
        # dictionary
        return username

    # Customizes form validation for the username field.
    def clean_first_name(self):
        # Confirms that the username is not already present in the
        # User model database.
        firstname = self.cleaned_data.get('first_name')
        if not firstname:
            raise forms.ValidationError("Your first name cannot be empty.")

        # Generally return the cleaned data we got from the cleaned_data
        # dictionary
        return firstname

    # Customizes form validation for the username field.
    def clean_last_name(self):
        # Confirms that the username is not already present in the
        # User model database.
        lastname = self.cleaned_data.get('last_name')
        if not lastname:
            raise forms.ValidationError("Your last name cannot be empty.")

        # Generally return the cleaned data we got from the cleaned_data
        # dictionary
        return lastname

    def save(self, commit=True):
        userprofile = super(RegistrationForm, self).save(commit=False)
        new_user = User.objects.create_user(username=self.cleaned_data['username'],
                                            password=self.cleaned_data['password_1'])
        userprofile.password = self.cleaned_data['password_1']
        userprofile.user = new_user
        if commit:
            new_user.save()
            userprofile.save()

        return userprofile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', 'password', 'gmail_id', 'friends', 'contacts', 'threads', 'username')
        widgets = {
            'bio': forms.Textarea(attrs={'cols': 40 , 'rows': 4})
        }

    picture = forms.FileField(required=False)