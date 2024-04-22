from django.shortcuts import render, redirect
from .models import Investment, Transaction,InvestmentGroup
from django.contrib.auth.decorators import user_passes_test
from .forms import InvestmentForm, TransactionForm,InvestmentGroupForm,UserSelectionForm
from datetime import date, timedelta
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
import plotly.express as px
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import io
from collections import defaultdict
from django.db.models import Sum
from django.utils import timezone
from django.shortcuts import render
from io import BytesIO
from PIL import Image
from django.db.models import Sum
import plotly.express as px
import base64
import matplotlib.pyplot as plt

import urllib, base64
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import F
from datetime import timedelta
import json
def home(request):
    # Your view logic here
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        # Get the username and password from the form
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # If the user is valid, log them in
            login(request, user)

            # Redirect the user to the dashboard or any other desired page
            return redirect('dashboard')  # Replace 'dashboard' with the name of your dashboard URL pattern
        else:
            # If the user is not valid, return an error message or render the login page again
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    else:
        return render(request, 'login.html')

@login_required
def add_investment(request):
    if request.method == 'POST':
        form = InvestmentForm(request.POST)
        if form.is_valid():
            investment = form.save(commit=False)
            investment.user = request.user
            investment.principal = investment.amount_invested
            investment.save()

            # Set the investment_group using the selected investment_groups
            investment_group = form.cleaned_data['investment_group']
            investment.investment_group.set(investment_group)

            investment.save()
            print("Investment saved successfully!")  # Add this line for debugging
            return redirect('investment_list')
        else:
            print("Form has errors:", form.errors)  # Add this line for debugging
    else:
        form = InvestmentForm()
    return render(request, 'add_investment.html', {'form': form})

@login_required
def investment_list(request):
    investments = Investment.objects.filter(user=request.user).order_by('investment_start_date')
    
    return render(request, 'investment_list.html', {'investments': investments})

@login_required
def add_transaction(request):
    investments = Investment.objects.all()
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            investment = transaction.investment
            transaction.added_by = request.user  # Set the added_by field to the current user

            # Handle deposits and withdrawals
            if transaction.transaction_type == 'deposit':
                investment.principal += transaction.amount

            else:
                investment.principal -= transaction.amount

            if investment.principal > 0:
               messages.warning(request, f"Next repayment is expected on {investment.next_repayment_date.strftime('%b %d, %Y')}.")



            investment.save()
            transaction.save()
            return redirect('transaction_list')
    
        else:
         print("Form has errors:", form.errors)  # Add this line for debugging
    else:
        form = TransactionForm()
    return render(request, 'add_transaction.html', {'form': form, 'investments': investments})



@login_required
def transaction_list(request):
    investments = Investment.objects.all()
    transactions = Transaction.objects.all()
    return render(request, 'transaction_list.html', {'investments': investments, 'transactions': transactions})
def is_admin(user):
    return user.is_superuser

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Add logic for the admin dashboard here
    return render(request, 'admin_dashboard.html')

@login_required
@staff_member_required
def manage_users(request):
    # Fetch all user objects from the database
    users = User.objects.all()

    return render(request, 'manage_users.html', {'users': users})

import numpy as np  # Import numpy library for logarithmic scaling

@user_passes_test(lambda user: user.is_superuser)
@user_passes_test(lambda user: user.is_superuser)
def dashboard(request):
    # Fetch all investments for all users
    investments = Investment.objects.all()

    # Calculate the total number of investments, users, transactions, and groups
    total_investments = investments.count()
    total_users = User.objects.count()
    total_transactions = Transaction.objects.count()
    total_groups = InvestmentGroup.objects.count()

    # Calculate total investment amounts including deposits
    investment_data = []
    for investment in investments:
        deposit_total = Transaction.objects.filter(investment=investment, transaction_type='deposit').aggregate(total_deposit=Sum('amount'))['total_deposit']
        if deposit_total is None:
            deposit_total = 0
        total_investment = investment.amount_invested + deposit_total
        investment_data.append((investment.investment_name, total_investment / 100000))

    # Unpack the investment data for plotting
    if investment_data:
        labels, amounts = zip(*investment_data)
    else: 
        labels, amounts = [], []   

    # Set Seaborn style
    sns.set(style="whitegrid")

    # Create the bar graph with Seaborn
    plt.figure(figsize=(12, 8))  # Adjust the figure size as needed
    ax = sns.barplot(x=labels, y=amounts, palette="viridis")  # Use a different color palette if needed
    ax.set_yscale("log")  # Set a logarithmic scale for the y-axis
    ax.set_ylabel('Investment in Millions')
    ax.set_title('Portfolio Composition')

    # Adjust x-axis tick labels for better visibility  
    plt.xticks(rotation=45, ha='right', fontsize=12)  # Increase font size for better visibility
    plt.subplots_adjust(bottom=0.3)  # Increase the bottom margin to accommodate rotated labels

    # Annotate each bar with its corresponding investment amount
    for bar, amount in zip(ax.patches, amounts):
        ax.annotate(f'{amount:.2f}', (bar.get_x() + bar.get_width() / 2, bar.get_height()), ha='center', va='bottom')

    # Add legend
    legend = ax.legend(labels=labels, title="Investments", title_fontsize="12", loc='upper right')
    legend.get_frame().set_linewidth(2)  # Set legend border thickness

    # Convert the plot to an image
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = urllib.parse.quote(base64.b64encode(img.read()))

    return render(request, 'dashboard.html', {
        'investments': investments,
        'plot_url': plot_url,
        'total_investments': total_investments,
        'total_users': total_users,
        'total_transactions': total_transactions,
        'total_groups': total_groups,
    })
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from .models import Investment, Transaction

def calculate_daily_schedule(investment, transactions):
    daily_schedule = []
    cumulative_interest_earned = Decimal('0.00')
    today = timezone.now().date()

    def update_principal(transaction_date, previous_balance):
        balance = previous_balance
        for transaction in transactions:
            if transaction.transaction_date == transaction_date:
                if transaction.transaction_type == 'deposit':
                    balance += transaction.amount
                else:
                    balance -= transaction.amount
        return balance

    months_to_add = investment.investment_period
    end_date = investment.investment_start_date + relativedelta(months=months_to_add)
    days_in_period = (end_date - investment.investment_start_date).days
    daily_interest_rate = (investment.interest_rate / 365) / 100

    # Initialize the previous day's cumulative balance
    principal = investment.amount_invested

    for day in range(days_in_period):
        previous_principal = principal
        installment_date = investment.investment_start_date + timedelta(days=day)
        interest_earned = principal * daily_interest_rate

        transaction_amount = Decimal('0.00')
        reduction_amount = Decimal('0.00')

        for transaction in transactions:
            if transaction.transaction_date == installment_date:
                if transaction.transaction_type == 'deposit':
                    transaction_amount += transaction.amount
                    investment.amount_invested += transaction_amount
                else:
                    reduction_amount += transaction.amount

        principal = update_principal(installment_date, previous_principal)
        cumulative_interest_earned += interest_earned
        cumulative_available_balance = principal + interest_earned
        cumulative_available_balance -= reduction_amount

        daily_schedule.append((
            installment_date,
            investment.amount_invested,
            transaction_amount,
            principal,
            interest_earned,
            cumulative_available_balance,
            reduction_amount,
        ))

        # Update the previous day's cumulative balance for the next day
        principal+=interest_earned

    return daily_schedule

def calculate_investment_schedule(investment_id, period, transactions=None):
    investment = Investment.objects.get(id=investment_id)
    investment_schedule = []
    today = timezone.now().date()

   
    

    # If transactions are not provided, get them from the database
    if transactions is None:
        transactions = Transaction.objects.filter(investment=investment).order_by('created_at')

    # Initialize the principal and interest earned to the original investment amount
    principal = investment.amount_invested
    cumulative_available_balance = Decimal('0.00')

    if period == 'daily':
        investment_schedule = calculate_daily_schedule(investment, transactions)

    elif period == 'weekly':
        days_in_week = 7
        week_investment=principal
        
        week_schedule = calculate_daily_schedule(investment, transactions)
        week_start_date = investment.investment_start_date
        # Calculate the number of days in the investment period
        months_to_add = investment.investment_period
        end_date = investment.investment_start_date + relativedelta(months=months_to_add)
        investment_start_date = investment.investment_start_date  # Replace with your actual start date
        
        days_in_period = (end_date - investment_start_date).days

# Calculate the number of weeks in the investment period
        weeks_in_period = days_in_period // 7

        for week in range(weeks_in_period):
            week_interest_earned = Decimal('0.00')  # Initialize weekly interest
            week_end_date = week_start_date + timedelta(weeks=1)

            for item in week_schedule:
                date, investment.amount_invested, _, _, interest_earned, available_balance, _ = item
                if week_start_date <= date < week_end_date:
                    week_interest_earned += interest_earned
                

            # Calculate the deposit for the current week
            week_deposit = sum([transaction.amount for transaction in transactions if
                                transaction.transaction_date >= week_start_date and
                                transaction.transaction_date < week_end_date and
                                transaction.transaction_type == 'deposit'])

            # Calculate the reduction amount for the current week
            week_reduction_amount = sum([transaction.amount for transaction in transactions if
                                         transaction.transaction_date >= week_start_date and
                                         transaction.transaction_date < week_end_date and
                                         transaction.transaction_type != 'deposit'])

            principal += week_deposit
            week_start_date = week_end_date
            week_investment+=week_deposit

            cumulative_available_balance = principal + week_interest_earned
            cumulative_available_balance -= week_reduction_amount

            investment_schedule.append((week_start_date, week_investment, week_deposit, principal,
                                        week_interest_earned, cumulative_available_balance, week_reduction_amount))
            principal+=week_interest_earned

    elif period == 'monthly':
        days_in_month = 30
        month_investment=principal
       
        month_schedule = calculate_daily_schedule(investment, transactions)
        month_start_date = investment.investment_start_date

        for month in range(investment.investment_period):
            month_interest_earned = Decimal('0.00')  # Initialize monthly interest
            month_end_date = month_start_date + relativedelta(months=1)

            for item in month_schedule:
                date, _, _, _, interest_earned, available_balance, _ = item
                if month_start_date <= date < month_end_date:
                    month_interest_earned += interest_earned

            # Calculate the deposit for the current month
            month_deposit = sum([transaction.amount for transaction in transactions if
                                 transaction.transaction_date >= month_start_date and
                                 transaction.transaction_date < month_end_date and
                                 transaction.transaction_type == 'deposit'])

            # Calculate the reduction amount for the current month
            month_reduction_amount = sum([transaction.amount for transaction in transactions if
                                          transaction.transaction_date >= month_start_date and
                                          transaction.transaction_date < month_end_date and
                                          transaction.transaction_type != 'deposit'])

            principal += month_deposit
            month_start_date = month_end_date
            month_investment+=month_deposit
            

            cumulative_available_balance = principal + month_interest_earned
            cumulative_available_balance -= month_reduction_amount

            investment_schedule.append((month_start_date, month_investment, month_deposit, principal,
                                        month_interest_earned, cumulative_available_balance, month_reduction_amount))
            principal+=month_interest_earned

    return investment_schedule




@login_required
def investment_detail(request, investment_id):
    investment = Investment.objects.get(id=investment_id)
    transactions = Transaction.objects.filter(investment=investment)
    investment_groups = investment.investment_group.all()  # Retrieve associated investment groups

    return render(request, 'investment_detail.html', {
        'investment': investment,
        'transactions': transactions,
        'investment_groups': investment_groups,  # Pass investment groups to the template
    })


@login_required
def schedule(request, investment_id):
    investment = Investment.objects.get(id=investment_id)

    investment_groups = investment.investment_group.all()
    # Call the calculate_investment_schedule function to get the investment_schedule
    period = request.POST.get('period', 'monthly')  # Default to 'monthly' if 'period' is not specified
    investment_schedule = calculate_investment_schedule(investment_id, period)

    return render(request, 'schedule.html', {
        'investment_schedule': investment_schedule,
            'investment': investment,
            'period': period,
            'investment_groups': investment_groups,
    })
def delete_investment(request, investment_id):
    investment = get_object_or_404(Investment, id=investment_id)

    if request.method == 'POST':
        # Delete the investment
        investment.delete()
        return redirect('investment_list')

    return render(request, 'delete_investment.html', {'investment': investment})
@login_required
def edit_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    investments = Investment.objects.all()

    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            new_transaction = form.save(commit=False)
            investment = new_transaction.investment

            # Handle deposits and withdrawals
            if new_transaction.transaction_type == 'deposit':
                investment.principal += new_transaction.amount - transaction.amount
                investment.deposits += new_transaction.amount - transaction.amount
            else:
                investment.principal -= new_transaction.amount - transaction.amount
                investment.withdrawals += new_transaction.amount - transaction.amount

            investment.save()
            new_transaction.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction)
    return render(request, 'edit_transaction.html', {'form': form, 'investments': investments, 'transaction': transaction})

@login_required
def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)

    if request.method == 'POST':
        investment = transaction.investment

        # Handle deposits and withdrawals
        if transaction.transaction_type == 'deposit':
            investment.principal -= transaction.amount
            investment.deposits -= transaction.amount
        else:
            investment.principal += transaction.amount
            investment.withdrawals -= transaction.amount

        investment.save()
        transaction.delete()
        return redirect('transaction_list')

    return render(request, 'delete_transaction.html', {'transaction': transaction})
@login_required
def edit_investment(request, investment_id):
    investment = get_object_or_404(Investment, id=investment_id)

    if request.method == 'POST':
        form = InvestmentForm(request.POST, instance=investment)
        if form.is_valid():
            investment = form.save(commit=False)
            investment.principal = investment.amount_invested
            investment.principal = investment.amount_invested
            investment.save()

            # Set the investment_group using the selected investment_groups
            investment_group = form.cleaned_data['investment_group']
            investment.investment_group.set(investment_group)

            investment.save()
            print("Investment saved successfully!")  # Add this line for debugging
            return redirect('investment_list')
        else:
            print("Form has errors:", form.errors)  # Add this line for debugging
        
    else:
        form = InvestmentForm(instance=investment)
    return render(request, 'edit_investment.html', {'form': form})
import pandas as pd
from django.http import HttpResponse

def download_schedule(request, investment_id):
    # Fetch the investment and its schedule
    investment = Investment.objects.get(id=investment_id)
    period = request.GET.get('period', 'monthly')
    investment_schedule = calculate_investment_schedule(investment_id, period)

    # Prepare the DataFrame
    df = pd.DataFrame(investment_schedule, columns=['Date', 'Original Principal', 'Deposit on Principal', 'New Principal', 'Interest Earned', 'Available Balance', 'Reduction'])

    # Format numerical columns with commas and two decimal points
    df['Original Principal'] = df['Original Principal'].apply(lambda x: f'{x:,.2f}')
    df['Deposit on Principal'] = df['Deposit on Principal'].apply(lambda x: f'{x:,.2f}')
    df['New Principal'] = df['New Principal'].apply(lambda x: f'{x:,.2f}')
    df['Interest Earned'] = df['Interest Earned'].apply(lambda x: f'{x:,.2f}')
    df['Available Balance'] = df['Available Balance'].apply(lambda x: f'{x:,.2f}')
    df['Reduction'] = df['Reduction'].apply(lambda x: f'{x:,.2f}')

    # Create an Excel file
    excel_file_name = f'investment_schedule_{investment_id}.xlsx'
    df.to_excel(excel_file_name, index=False)

    # Set up the response with the Excel file
    with open(excel_file_name, 'rb') as excel_file:
        response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{excel_file_name}"'

    return response

from django.contrib.auth.models import User
from .forms import UserForm
@login_required
def add_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_users')
    else:
        form = UserForm()
    return render(request, 'add_user.html', {'form': form})
@login_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('manage_users')
    else:
        form = UserForm(instance=user)

    return render(request, 'edit_user.html', {'form': form})
@login_required
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
    except User.DoesNotExist:
        # Handle the case when the user with the given id does not exist
        pass

    return redirect('manage_users')

from .forms import UserProfileForm,UserEditForm
from .models import UserProfile

@login_required
def profile_edit(request):
    user = request.user
    try:
        user_profile = user.userprofile
    except UserProfile.DoesNotExist:
        # If UserProfile does not exist, create a new one for the user
        user_profile = UserProfile(user=user)
        user_profile.save()

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile_edit')
    else:
        user_form = UserEditForm(instance=user)
        profile_form = UserProfileForm(instance=user_profile)

    return render(request, 'profile_edit.html', {'user_form': user_form, 'profile_form': profile_form})


# ... (your other imports and code)
@login_required
def investment_data(request):
    if request.method == 'GET':
        selected_group_id = request.GET.get('group')
        selected_chart_types = request.GET.getlist('gadgets')

        # Retrieve investment groups and their investments
        investment_groups = InvestmentGroup.objects.all()

        # Get the selected group or use the first group as the default
        selected_group = InvestmentGroup.objects.filter(id=selected_group_id).first()

        # Initialize variables to store data for charts
        line_chart_image_base64 = None
        pie_chart_image_base64 = None

        if selected_group:
            # Fetch investments for the selected group
            investments = selected_group.investment_set.all()

            # Initialize cumulative totals and date labels
            cumulative_balances = []
            date_labels = []

            for investment in investments:
                investment_schedule = calculate_investment_schedule(investment.id, period='monthly')

                # Extract the dates and cumulative balances for the line chart
                dates = [entry[0].strftime('%b %Y') for entry in investment_schedule]
                balances = [entry[5] for entry in investment_schedule]
                

                # Add the balances to the cumulative totals
                if not cumulative_balances:
                    cumulative_balances = balances
                else:
                    cumulative_balances = [sum(x) for x in zip(cumulative_balances, balances)]

                # Set the date labels (using the first investment's dates)
                if not date_labels:
                    date_labels = dates

            # Prepare data for the report
            report_data = [{
                'group_name': selected_group.name,
                'date_labels': date_labels,
                'cumulative_balances': cumulative_balances,
            }]

            if 'line_chart' in selected_chart_types:
                # Create the line chart using matplotlib
                plt.figure(figsize=(10, 6))  # Width=10 inches, Height=6 inches
                plt.plot(date_labels, cumulative_balances, marker='o', color='b')
                plt.xlabel('Date')
                plt.ylabel('Cumulative Balance')
                plt.title('Cumulative Available Balance Over Time\nGroup: {}'.format(selected_group.name))
                plt.xticks(rotation=45)

                # Save the plot as an image
                buf = BytesIO()
                plt.savefig(buf, format='png')
                plt.close()
                buf.seek(0)
                line_chart_image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

            if 'pie_chart' in selected_chart_types:
                # Calculate the cumulative interest and initial investment amount for the selected group
                initial_investment_total = sum([investment.amount_invested for investment in investments])
                 # Calculate the total deposits for the selected group
                total_deposits = sum([sum([transaction.amount for transaction in investment.transaction_set.filter(transaction_type='deposit')]) for investment in investments])
                initial_investment_total +=total_deposits
                cumulative_interest_total = cumulative_balances[-1] - initial_investment_total
                

                # Create data for the pie chart
                labels = ['Initial Investment', 'Cumulative Interest']
                values = [initial_investment_total, cumulative_interest_total]

                # Create the pie chart using matplotlib
                plt.figure(figsize=(10, 10))
                plt.pie(values, labels=labels, autopct='%1.1f%%')
                plt.title('Initial Investment and Cumulative Interest\nGroup: {}'.format(selected_group.name))

                # Save the plot as an image
                buf = BytesIO()
                plt.savefig(buf, format='png')
                plt.close()
                buf.seek(0)
                pie_chart_image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        return render(request, 'investment_data.html', {
            'investment_groups': investment_groups,
            'selected_group': selected_group,
            'selected_chart_types': selected_chart_types,
            'line_chart_image': line_chart_image_base64,
            'pie_chart_image': pie_chart_image_base64,
            'report_data': report_data,  # Add report_data to the context
        })

    return render(request, 'investment_data.html')



from .models import AccessLog

@login_required
def access_logs(request):
    logs = AccessLog.objects.all()
    return render(request, 'access_logs.html', {'logs': logs})

@login_required
def report(request):
     # Retrieve investment groups and their investments
    investment_groups = InvestmentGroup.objects.all()
    return render(request, 'report.html', {'investment_groups': investment_groups})


@login_required
def create_investment_group(request):
    if request.method == 'POST':
        form = InvestmentGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            group.members.add(request.user)  # Add the creator as a member
            return redirect('group_list')  # Redirect to the group list page
    else:
        form = InvestmentGroupForm()
    return render(request, 'create_group.html', {'form': form})

@login_required
def edit_investment_group(request, group_id):
    # Fetch the existing investment group to be edited
    group = InvestmentGroup.objects.get(id=group_id)

    if request.method == 'POST':
        form = InvestmentGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()  # Save the updated group details
            return redirect('group_list')  # Redirect to the group list page after editing
    else:
        form = InvestmentGroupForm(instance=group)  # Prepopulate the form with existing data

    return render(request, 'edit_group.html', {'form': form, 'group': group})


@login_required
def group_list(request):
    groups = InvestmentGroup.objects.all()
    return render(request, 'group_list.html', {'groups': groups})

@login_required
def join_group(request, group_id):
    group = InvestmentGroup.objects.get(id=group_id)
    group.members.add(request.user)
    return redirect('group_list')

@login_required
def leave_group(request, group_id):
    group = InvestmentGroup.objects.get(id=group_id)
    group.members.remove(request.user)
    return redirect('group_list')

@login_required
def user_selection(request, group_id):
    users = User.objects.all()  # Fetch all users
    group = InvestmentGroup.objects.get(id=group_id)

    if request.method == 'POST':
        form = UserSelectionForm(request.POST)
        if form.is_valid():
            selected_users = form.cleaned_data['users']
            group.members.set(selected_users)  # Update the group's members with the selected users
            return redirect('group_list')
    else:
        form = UserSelectionForm()

    return render(request, 'user_selection.html', {'form': form, 'users': users, 'group': group})


@login_required
def group_join(request, group_id):
    group = InvestmentGroup.objects.get(id=group_id)

    if request.method == 'POST':
        selected_users = request.POST.getlist('selected_users')
        # Process selected_users and attach them to the group
        for user_id in selected_users:
            user = User.objects.get(id=user_id)
            group.members.add(user)
        return redirect('group_list')

    return render(request, 'group_join.html', {'group': group, 'group_id': group_id})

@login_required
def group_details(request, group_id):
    group = InvestmentGroup.objects.get(id=group_id)
    members = group.members.all()  # Fetch all members of the group

    return render(request, 'group_details.html', {'group': group, 'members': members})

@login_required
def delete_group(request, group_id):
    group = InvestmentGroup.objects.get(id=group_id)
    if request.method == 'POST':
        group.delete()
        return redirect('group_list')
    return render(request, 'delete_group.html', {'group': group})

@login_required
def add_members(request, group_id):
    group = InvestmentGroup.objects.get(id=group_id)

    if request.method == 'POST':
        selected_users = request.POST.getlist('selected_users')
        for user_id in selected_users:
            user = User.objects.get(id=user_id)
            group.members.add(user)
        return redirect('group_details', group_id=group_id)

    users = User.objects.exclude(id__in=group.members.all())
    return render(request, 'add_members.html', {'group': group, 'users': users})

def investment_report(request):
    # Retrieve investment groups and their investments
    investment_groups = InvestmentGroup.objects.all()
    
    # Create a list to store the report data
    report_data = []

    for group in investment_groups:
        investments = group.investment_set.all()  # Get investments for the group
        
        # Initialize cumulative totals
        initial_investment_total = 0
        cumulative_interest_total = 0
        final_investment_total = 0

        # Calculate cumulative totals for each investment in the group
        for investment in investments:
            # Calculate the investment schedule for the entire investment period (daily)
            investment_schedule = calculate_investment_schedule(investment.id, period='daily')

            # Calculate the cumulative interest and final investment amount up to the current date
            today = timezone.now().date()
            cumulative_interest = 0
            final_investment = 0
            total_deposits = 0  # Initialize total deposits for this investment

            for entry in investment_schedule:
                date, _, deposits, _, interest_earned, available_balance, _ = entry
                if date <= today:
                    cumulative_interest += interest_earned
                    final_investment = available_balance  # The available balance on the current date
                    total_deposits += deposits

            # Add the initial investment amount and total deposits to the initial_investment_total
            initial_investment_total += (investment.amount_invested + total_deposits)

            cumulative_interest_total += cumulative_interest
            final_investment_total += final_investment

        # Append data for the current group to the report_data list
        report_data.append({
            'group_name': group.name,
            'investments': investments,
            'initial_investment_total': initial_investment_total,
            'cumulative_interest_total': cumulative_interest_total,
            'final_investment_total': final_investment_total,
        })

    return render(request, 'investment_report.html', {'report_data': report_data})

from decimal import Decimal
from dateutil.relativedelta import relativedelta
from datetime import timedelta
from .models import Investment, Transaction, InvestmentGroup

from collections import defaultdict
def calculate_group_schedule(group_id, period):
    group = InvestmentGroup.objects.get(id=group_id)
    investments = Investment.objects.filter(investment_group=group)

    # Calculate the total initial investment amount in the group
    initial_investment_total = sum(investment.amount_invested for investment in investments)

    # Find the investment with the lowest start date
    lowest_start_date_investment = min(investments, key=lambda x: x.investment_start_date)

    # Use the lowest start date investment's interest rate and investment period
    interest_rate = lowest_start_date_investment.interest_rate
    investment_period = lowest_start_date_investment.investment_period

    # Define a dictionary to store the aggregated group schedule
    group_schedule = defaultdict(lambda: [initial_investment_total, 0, 0, 0, 0, 0])

    # Initialize the principal and interest earned to the original investment amount
    principal = initial_investment_total
    interest_earned = 0

    # Function to update principal based on transactions
    def update_principal(transaction_date, previous_balance):
        balance = previous_balance

        for investment in investments:
            transactions = Transaction.objects.filter(investment=investment).order_by('created_at')
            for transaction in transactions:
                if transaction.transaction_date == transaction_date:
                    if transaction.transaction_type == 'deposit':
                        balance += transaction.amount
                    else:
                        balance -= transaction.amount

        return balance

    # Calculate schedule based on the selected period
    if period == 'monthly':
        for month in range(investment_period):
            installment_date = lowest_start_date_investment.investment_start_date + relativedelta(months=month)
            previous_principal = principal

            # Calculate total deposits for the current month
            deposits_for_period = sum(
                [Transaction.objects.filter(
                    investment=investment,
                    transaction_date__month=installment_date.month,
                    transaction_date__year=installment_date.year,
                    transaction_type='deposit')
                .aggregate(total_deposit=Sum('amount'))['total_deposit'] or 0
                for investment in investments])

            principal = update_principal(installment_date, previous_principal)
            principal += deposits_for_period
            initial_investment_total += deposits_for_period
            # Calculate total reductions for the current month
            reduction_amount = sum(
                [transaction.amount for investment in investments for transaction in Transaction.objects.filter(investment=investment)
                 if transaction.transaction_date.month == installment_date.month and
                 transaction.transaction_date.year == installment_date.year and
                 transaction.transaction_type != 'deposit'])
            principal -= reduction_amount

            payment = principal / investment_period
            interest_earned = (principal * (interest_rate / 12)) / 100

            # Update the group_schedule for the current month
            group_schedule[installment_date][1] += deposits_for_period  # Total Deposits
            group_schedule[installment_date][2] += reduction_amount  # Total Reductions
            group_schedule[installment_date][3] += interest_earned
            group_schedule[installment_date][4] += payment
            group_schedule[installment_date][5] = principal + interest_earned  # Store cumulative available balance

            # Update principal for the next month's calculation
            group_schedule_list = [(date, values[0], values[1], values[2], values[3], values[4], values[5]) for date, values in group_schedule.items()]

            principal += interest_earned

    elif period == 'weekly':
        for week in range(investment_period * 4):  # Assuming 4 weeks per month
            start_date = lowest_start_date_investment.investment_start_date + timedelta(weeks=week)
            end_date = start_date + timedelta(weeks=1)
            previous_principal = principal

            # Calculate total deposits for the current week
            deposits_for_period = sum(
                [transaction.amount for investment in investments for transaction in Transaction.objects.filter(investment=investment)
                 if transaction.transaction_date >= start_date and
                 transaction.transaction_date < end_date and
                 transaction.transaction_type == 'deposit'])
            
            principal += deposits_for_period
            initial_investment_total += deposits_for_period
            # Calculate total reductions for the current week
            reduction_amount = sum(
                [transaction.amount for investment in investments for transaction in Transaction.objects.filter(investment=investment)
                 if transaction.transaction_date >= start_date and
                 transaction.transaction_date < end_date and
                 transaction.transaction_type != 'deposit'])
            principal -= reduction_amount

            payment = principal / investment_period
            interest_earned = (principal * (interest_rate / 52)) / 100

            # Update the group_schedule for the current week
            group_schedule[end_date][1] += deposits_for_period  # Total Deposits
            group_schedule[end_date][2] += reduction_amount  # Total Reductions
            group_schedule[end_date][3] += interest_earned
            group_schedule[end_date][4] += payment
            group_schedule[end_date][5] = principal + interest_earned  # Store cumulative available balance

            # Update principal for the next week's calculation
            group_schedule_list = [(date, values[0], values[1], values[2], values[3], values[4], values[5]) for date, values in group_schedule.items()]

            principal += interest_earned

    # Calculate schedule based on the selected period
    elif period == 'daily':
        months_to_add = lowest_start_date_investment.investment_period
        end_date = lowest_start_date_investment.investment_start_date + relativedelta(months=months_to_add)

        days_in_period = (end_date - lowest_start_date_investment.investment_start_date).days
        daily_interest_rate = (lowest_start_date_investment.interest_rate / 365) / 100

        for day in range(days_in_period):
            installment_date = lowest_start_date_investment.investment_start_date + timedelta(days=day)
            previous_principal = principal
            
            # Get the transaction amount for the current date
            transaction_amount = Decimal('0.00')
            reduction_amount = Decimal('0.00')

            for investment in investments:
                transactions = Transaction.objects.filter(investment=investment)
                for transaction in transactions:
                    if transaction.transaction_date == installment_date:
                        if transaction.transaction_type == 'deposit':
                            transaction_amount += transaction.amount
                            principal += transaction.amount
                            # Update the initial investment total with deposits
                            initial_investment_total += transaction.amount
                        else:
                            reduction_amount += transaction.amount
                            principal -= transaction.amount
            
             # Calculate payment, interest, and principal paid for the current day
            
            payment = principal / days_in_period
            interest_earned = principal * daily_interest_rate
            principal_paid = payment             

            # Update the group_schedule for the current day
            group_schedule[installment_date][1] += transaction_amount  # Total Deposits
            group_schedule[installment_date][2] += reduction_amount  # Total Reductions
            group_schedule[installment_date][3] += interest_earned
            group_schedule[installment_date][4] += principal_paid
            group_schedule[installment_date][5] = principal + interest_earned  # Store cumulative available balance

            principal+=interest_earned    

        # Convert the group_schedule dictionary to a list of tuples
        group_schedule_list = [(date, values[0], values[1], values[2], values[3], values[4], values[5]) for date, values in group_schedule.items()]
        
    # Sort the group_schedule by date
    group_schedule_list.sort()

    # Returning the group_schedule as a list of tuples
    return group_schedule_list



def group_investment_schedule(request, group_id):
    # Retrieve the group and its investments
    group = get_object_or_404(InvestmentGroup, id=group_id)
    investments = group.investment_set.all()
    
    # Get the selected period from the request, defaulting to 'monthly' if not specified
    period = request.GET.get('period', 'monthly')
    
    # Calculate the group schedule for the selected period
    group_schedule = calculate_group_schedule(group.id, period)

    return render(request, 'group_investment_schedule.html', {
        'group': group,
        'investments': investments,
        'group_schedule': group_schedule,  # Pass the group schedule to the template
        'selected_period': period,  # Pass the selected period to the template
    })


@login_required
def investment_group_details(request, group_id):
    # Retrieve the investment group
    group = get_object_or_404(InvestmentGroup, id=group_id)

    # Retrieve all investments in the group
    investments = group.investment_set.all()

    return render(request, 'investment_group_details.html', {'group': group, 'investments': investments})

def investment_group_detail(request, group_id):
    group = get_object_or_404(InvestmentGroup, pk=group_id)
    investments = Investment.objects.filter(investment_group=group)
    transactions = Transaction.objects.filter(investment__in=investments)

    investment_data = []

    for investment in investments:
        investment_schedule = calculate_investment_schedule(investment.id, period='daily')

        # Initialize cumulative totals
        initial_investment_total = 0
        cumulative_interest = 0
        total_deposits = 0

        # Calculate the total interest earned for this investment up to the current date
        today = timezone.now().date()
        for entry in investment_schedule:
            date, _, deposits, _, interest_earned, available_balance, _ = entry
            if date <= today:
                cumulative_interest += interest_earned
                total_deposits += deposits

        # Add deposits to the investment amount
        total_deposits+=investment.amount_invested
        total_investment_amount = investment.amount_invested + total_deposits + cumulative_interest

        investment_data.append({
            'investment': investment,
            'investment_schedule': investment_schedule,
            'total_deposits': total_deposits,
            'total_interest_earned': cumulative_interest,
            'total_investment_amount': total_investment_amount,
        })
        
    
    
    # Calculate totals outside the loop
    total_amount = sum([item['total_investment_amount'] for item in investment_data])
    total_depot = sum([item['total_deposits'] for item in investment_data])
    total_interest= sum([item['total_interest_earned'] for item in investment_data])
    total_invested = sum([item['investment'].amount_invested for item in investment_data])



    return render(request, 'investment_group_data.html', {
        'group': group,
        'investment_data': investment_data,
        'total_amount': total_amount,
        'total_depot': total_depot,
        'total_interest': total_interest,
        'total_invested': total_invested,
    })