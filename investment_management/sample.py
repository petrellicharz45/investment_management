def calculate_investment_schedule(investment_id, period, transactions=None):
    investment = Investment.objects.get(id=investment_id)
    investment_schedule = []

    # Function to update principal based on transactions
    def update_principal(transaction_date, previous_balance):
        balance = previous_balance

        for transaction in transactions:
            if transaction.transaction_date == transaction_date:
                if transaction.transaction_type == 'deposit':
                    balance += transaction.amount
                else:
                    balance -= transaction.amount

        return balance

    # If transactions are not provided, get them from the database
    if transactions is None:
        transactions = Transaction.objects.filter(investment=investment).order_by('created_at')

    # Initialize the principal and interest earned to the original investment amount
    principal = investment.amount_invested
    interest_earned = 0
    cumulative_interest_earned = 0
    cumulative_available_balance = 0

    if period == 'monthly':
        month_deposit = Decimal('0.00')  # Initialize the deposit for the current month

        for month in range(investment.investment_period):
            installment_date = investment.investment_start_date + relativedelta(months=month)
            previous_principal = principal

            # Calculate the deposit for the current month
            month_deposit = sum([transaction.amount for transaction in transactions if
                                 transaction.transaction_date >= installment_date and
                                 transaction.transaction_date < installment_date + relativedelta(months=1) and
                                 transaction.transaction_type == 'deposit'])

            # Calculate the reduction amount for the current month
            month_reduction_amount = sum([transaction.amount for transaction in transactions if
                                        transaction.transaction_date >= installment_date and
                                        transaction.transaction_date < installment_date + relativedelta(months=1) and
                                        transaction.transaction_type != 'deposit'])

            principal = update_principal(installment_date, previous_principal)

            payment = principal / investment.investment_period
            interest_earned = (principal * (investment.interest_rate / 12)) / 100
            principal_paid = payment - (interest_earned / (investment.investment_period - month))
            cumulative_interest_earned += interest_earned

            investment.amount_invested += month_deposit
            principal += month_deposit

            cumulative_available_balance = principal + interest_earned
            cumulative_available_balance -= month_reduction_amount
            investment_schedule.append((installment_date, investment.amount_invested, month_deposit, principal,
                                        interest_earned, cumulative_available_balance, month_reduction_amount))

            # Update principal for next month's calculation
            principal += interest_earned

    elif period == 'weekly':
        week_deposit = Decimal('0.00')  # Initialize the deposit for the current week

        for week in range(investment.investment_period * 4):
            installment_date = investment.investment_start_date + timedelta(weeks=week)
            previous_principal = principal

            # Calculate the deposit for the current week
            week_deposit = sum([transaction.amount for transaction in transactions if
                                transaction.transaction_date >= installment_date and
                                transaction.transaction_date < installment_date + timedelta(weeks=1) and
                                transaction.transaction_type == 'deposit'])

            # Calculate the reduction amount for the current week
            week_reduction_amount = sum([transaction.amount for transaction in transactions if
                                        transaction.transaction_date >= installment_date and
                                        transaction.transaction_date < installment_date + timedelta(weeks=1) and
                                        transaction.transaction_type != 'deposit'])

            

            payment = principal / (investment.investment_period * 4)
            interest_earned = (principal * (investment.interest_rate / 52)) / 100
            principal_paid = payment - (interest_earned / (investment.investment_period * 4))
            cumulative_interest_earned += interest_earned
            
            
            principal+= week_deposit
            investment.amount_invested += week_deposit

            # Calculate cumulative available balance
            cumulative_available_balance =principal + interest_earned
            
            cumulative_available_balance -= week_reduction_amount

            investment_schedule.append((installment_date, investment.amount_invested, week_deposit, principal,
                                        interest_earned, cumulative_available_balance, week_reduction_amount))

            # Update principal for next week's calculation
            principal += interest_earned

    elif period == 'daily':
        months_to_add = investment.investment_period
        end_date = investment.investment_start_date + relativedelta(months=months_to_add)

        days_in_period = (end_date - investment.investment_start_date).days
        daily_interest_rate = (investment.interest_rate / 365) / 100

        for day in range(days_in_period):
            installment_date = investment.investment_start_date + timedelta(days=day)
            previous_principal = principal

            payment = principal / days_in_period
            interest_earned = principal * daily_interest_rate
            principal_paid = payment

            # Get the transaction amount for the current date
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

            investment_schedule.append((
                installment_date,
                investment.amount_invested,
                transaction_amount,
                principal,
                interest_earned,
                cumulative_available_balance,
                reduction_amount,
            ))

            # Update principal for next day's calculation
            principal += interest_earned

    # Returning the investment_schedule as a list of tuples
    return investment_schedule
