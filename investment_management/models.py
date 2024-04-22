from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from datetime import datetime, timedelta
from django.dispatch import receiver
class InvestmentGroup(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='investment_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        # Delete connected investments first
        Investment.objects.filter(investment_group=self).delete()
        super(InvestmentGroup, self).delete(*args, **kwargs)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    next_of_kin = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    def __str__(self):
        return self.user.username

# Signal to create a user profile when a new user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

# Signal to save the user profile when the user is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class Investment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    investment_name = models.CharField(max_length=1000)
    investment_period = models.PositiveIntegerField()
    interest_rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount_invested = models.DecimalField(max_digits=1000, decimal_places=2)
    principal = models.DecimalField(max_digits=1000, decimal_places=2)
    daily_interest = models.DecimalField(max_digits=1000, decimal_places=2, default=0)
    withdrawals = models.DecimalField(max_digits=1000, decimal_places=2, default=0)
    deposits = models.DecimalField(max_digits=1000, decimal_places=2, default=0)
    
    next_repayment_date = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)  # Ensure this line is present
    investment_group = models.ManyToManyField(InvestmentGroup, blank=True)
    investment_start_date = models.DateField(blank=True,null=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            # Only set the initial next_repayment_date if the instance is being created
            self.updated_at = datetime.now()  # Set the updated_at field here
            self.next_repayment_date = self.updated_at + timedelta(days=30)
        super().save(*args, **kwargs)
class Transaction(models.Model):
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10000, decimal_places=2)
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('ledger_fees', 'Ledger Fees'),
        ('interest', 'Interest'),
        ('bank_charges', 'Bank Charges'),
        ('others', 'Others')
    ]
    transaction_type = models.CharField(max_length=16, choices=TRANSACTION_TYPES)
    transaction_date=models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)

class AccessLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=255)    

