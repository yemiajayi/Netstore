from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django import forms
from django.forms import ModelForm
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal
from .models import Auction, Bid
from django.db.models import Q


# Create User form
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']


# Edit User form
class EditUserForm(UserChangeForm):

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']


# User login form
class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


# Auction form
class CreateAuctionForm(ModelForm):

    class Meta:

        model = Auction
        fields = ['title', 'description', 'deadline', 'min_price']

    def __init__(self, *args, **kwargs):
        super(CreateAuctionForm, self).__init__(*args, **kwargs)
        self.fields['min_price'] = forms.DecimalField(min_value=0.01, max_digits=10, decimal_places=2)

    def clean_deadline(self):

        deadline = self.cleaned_data['deadline']
        today = timezone.now()

        if deadline - today < timedelta(hours=72):
            raise forms.ValidationError("Min auction time is 72h")
        return deadline

    def clean_price(self):

        try:
            min_price = Decimal(self.cleaned_data['min_price'])
        except:
            raise forms.ValidationError("Please input a number")

        if min_price < 0.009:
            raise forms.ValidationError("Minimum price is 0.01")

        return min_price


# search form
class SearchForm(forms.Form):
    query = forms.CharField(max_length=300, required=False, label='')

    def search(self):
        cleaned_data = self.cleaned_data
        cleaned_query = cleaned_data.get('query', '')
        if cleaned_query:
            matching_auctions = Auction.objects.filter(
                Q(title__icontains=cleaned_query) | Q(description__icontains=cleaned_query))
        else:
            matching_auctions = Auction.objects.filter()

        return matching_auctions


# Auction Bidding form
class BiddingForm(forms.ModelForm):

    class Meta:
        model = Bid
        fields = ['bid']

    def __init__(self, *args, **kwargs):
        super(BiddingForm, self).__init__(*args, **kwargs)

        self.fields['bid'] = forms.DecimalField(min_value=0.01, max_digits=10, decimal_places=2)

    def clean_bid(self):
        try:
            bid = Decimal(self.cleaned_data['bid'])
        except:
            raise forms.ValidationError("Please input a number")

        if bid < 0.009:
            raise forms.ValidationError("Min bid is 0.01")
        return bid
