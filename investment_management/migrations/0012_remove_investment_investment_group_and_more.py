# Generated by Django 4.2.4 on 2023-09-14 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investment_management', '0011_remove_investment_owners_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='investment',
            name='investment_group',
        ),
        migrations.AddField(
            model_name='investment',
            name='investment_group',
            field=models.ManyToManyField(blank=True, to='investment_management.investmentgroup'),
        ),
    ]