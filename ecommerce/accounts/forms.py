# accounts/forms.py

from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        # Make sure your custom user model is referenced here
        model = CustomUser
        # Ensure all fields you want on the registration form are listed
        fields = ('username', 'email') # Add or remove fields as needed

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Define the Tailwind CSS classes you want to apply to every field
        tailwind_classes = "w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
        
        # Loop through all the fields in the form and add the CSS classes to their widgets
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': tailwind_classes})