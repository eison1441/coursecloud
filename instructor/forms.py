from django.contrib.auth.forms import UserCreationForm
from instructor.models import User
from django import forms


class InstructorCreateForm(UserCreationForm):

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control mb-3 text-warning-emphasis rounded-3"}),
        label="Password"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control mb-3 text-warning-emphasis rounded-3"}),
        label="Confirm Password"
    )

    class Meta:

        model=User

        fields=["username","email","password1","password2"]
        

        widgets={

            "username":forms.TextInput(attrs={"class":"form-control mb-3 mt-3 text-warning-emphasis rounded-3"}),
            "email":forms.EmailInput(attrs={"class":"form-control mb-3 mt-3 text-warning-emphasis rounded-3"}),
            # "first_name":forms.TextInput(attrs={"class":"form-control mb-3 mt-3 text-warning-emphasis rounded-3"}),
            
            
        }