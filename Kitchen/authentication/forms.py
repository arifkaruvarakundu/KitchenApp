# forms.py
from django import forms
from .models import Address

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            'street_address', 'city', 'zipcode', 'country', 'phone_number',
        ]
