from django import forms
from .models import Account,UserProfile

class RegistrationForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter Password',
        'class':'form-control',
    }))
    confirm_password=forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Confirm Password',
        'class':'form-control',
    }))
    email=forms.CharField(widget=forms.EmailInput(attrs={
        'placeholder':'Enter Email',
        'class':'form-control',
    }))
    first_name=forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':'Enter First Name',
        'class':'form-control',
    }))
    last_name=forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':'Enter Last Name',
        'class':'form-control',
    }))
    phone_number=forms.CharField(widget=forms.TextInput(attrs={
        'placeholder':'Enter Phone Number',
        'class':'form-control',
    }))
    newsletter_subscription = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={
        'class': 'form-check-input',
    }))
    class Meta:
        model=Account
        fields=['first_name','last_name','phone_number','email','password','newsletter_subscription']
            
    def clean(self):
        cleaned_data=super(RegistrationForm,self).clean()
        password=cleaned_data.get('password')
        confirm_password=cleaned_data.get('confirm_password')
        
        if password!=confirm_password:
            raise forms.ValidationError(
                "Password does not match!"
            )
            
class UserForm(forms.ModelForm):
    class Meta:
        model=Account
        fields=['first_name','last_name','phone_number']
    
    
class UserProfileForm(forms.ModelForm):
    class Meta:
        model=UserProfile
        fields=['address_line_1','address_line_2','city','state','country','profile_picture']
        
