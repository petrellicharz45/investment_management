from django import forms
from .models import Investment, Transaction, InvestmentGroup
from .models import UserProfile
from django.contrib.auth.models import User

class InvestmentForm(forms.ModelForm):
    investment_group= forms.ModelMultipleChoiceField(
        queryset=InvestmentGroup.objects.all(),  # Use InvestmentGroup queryset
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'custom-control-input'}),
        label='Investment Groups',
        to_field_name='id',  # Use the ID field as the value for the options
        required=False,      # Optional field
    )
    investment_start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Investment Start Date',
        required=True,
    )
    investment_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Investment Name',
        required=True,
    )
    investment_period = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        label='Investment Period (in months)',
        required=True,
    )
    interest_rate = forms.DecimalField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Interest Rate',
        required=True,
    )
    amount_invested = forms.DecimalField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Amount Invested',
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the label for each option in the owners field
        self.fields['investment_group'].label_from_instance = lambda obj: obj.name  # Adjust to use the appropriate attribute for InvestmentGroup

    class Meta:
        model = Investment
        fields = ['investment_group', 'investment_name', 'investment_period', 'interest_rate', 'amount_invested', 'investment_start_date']

class TransactionForm(forms.ModelForm):
    investment = forms.ModelChoiceField(
        queryset=Investment.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Select Investment',
        required=True,
    )
    amount = forms.DecimalField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Amount',
        required=True,
    )
    transaction_type = forms.ChoiceField(
        choices=Transaction.TRANSACTION_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Transaction Type',
        required=True,
    )

    transaction_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Transaction Date',
        required=True,
    )

    class Meta:
        model = Transaction
        fields = ['investment', 'amount', 'transaction_type','transaction_date']
from django.contrib.auth.models import User,Permission

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'is_active', 'is_staff', 'permissions']
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['next_of_kin', 'address', 'phone_number', 'profile_photo']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    # You can also customize individual form fields further if needed
    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        # Add any phone number validation here if necessary
        return phone_number
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    

class InvestmentGroupForm(forms.ModelForm):
    class Meta:
        model = InvestmentGroup
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter group name'})

class UserSelectionForm(forms.Form):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )       