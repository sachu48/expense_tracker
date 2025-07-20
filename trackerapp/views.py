from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Expense
from .forms import ExpenseForm
from django import forms
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from .models import MonthlyIncome
from .forms import MonthlyIncomeForm
from datetime import date


@login_required
def home(request):
    expenses = Expense.objects.filter(user=request.user)

    # Aggregate expenses by category
    category_data = expenses.values('category').annotate(total=Sum('amount'))

    labels = [entry['category'] for entry in category_data]
    data = [float(entry['total']) for entry in category_data]

    today = timezone.now().date()
    month_start = date(today.year, today.month, 1)

    # Fetch Monthly Income
    income_entry = MonthlyIncome.objects.filter(user=request.user, month=month_start).first()
    monthly_income = float(income_entry.income) if income_entry else 0

    # Calculate current month's expenses
    monthly_expense = Expense.objects.filter(
        user=request.user,
        date__year=today.year,
        date__month=today.month
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    return render(request, 'trackerapp/home.html', {
        'labels': labels,
        'data': data,
        'monthly_income': monthly_income,
        'monthly_expense': float(monthly_expense),
    })


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'trackerapp/register.html', {'form': form})

#class ExpenseForm(forms.ModelForm):
 #   class Meta:
  #      model = Expense
   #     fields = ['title', 'amount', 'category', 'date', 'description']

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, "Expense added!")  
            return redirect('view_expenses')  # ✅ Correct
  # redirect to the list after saving
    else:
        form = ExpenseForm()
    return render(request, 'trackerapp/add_expense.html', {'form': form})




@login_required
def view_expenses(request):
    # Base queryset
    expenses = Expense.objects.filter(user=request.user)

    # Get filters from request
    selected_category = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Apply category filter
    if selected_category:
        expenses = expenses.filter(category=selected_category)

    # Apply date range filter
    if start_date and end_date:
        expenses = expenses.filter(date__range=[start_date, end_date])

    # Totals for filtered and fixed ranges
    filtered_total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    start_of_month = today.replace(day=1)

    weekly_total = Expense.objects.filter(user=request.user, date__gte=start_of_week).aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_total = Expense.objects.filter(user=request.user, date__gte=start_of_month).aggregate(Sum('amount'))['amount__sum'] or 0
    overall_total = Expense.objects.filter(user=request.user).aggregate(Sum('amount'))['amount__sum'] or 0

    # Income Calculations
    total_income = MonthlyIncome.objects.filter(user=request.user).aggregate(Sum('income'))['income__sum'] or 0

    balance = total_income - overall_total  # Remaining balance

    categories = Expense.objects.filter(user=request.user).values_list('category', flat=True).distinct()

    context = {
        'expenses': expenses,
        'filtered_total': filtered_total,
        'weekly_total': weekly_total,
        'monthly_total': monthly_total,
        'overall_total': overall_total,
        'total_income': total_income,
        'balance': balance,
        'categories': categories,
        'selected_category': selected_category,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'trackerapp/view_expenses.html', context)

@login_required
def add_monthly_income(request):
    if request.method == 'POST':
        form = MonthlyIncomeForm(request.POST)
        if form.is_valid():
            income = form.cleaned_data['income']
            month_str = form.cleaned_data['month']  # e.g., "2025-07"
            try:
                # Convert to full date YYYY-MM-01
                month_date = datetime.strptime(month_str, "%Y-%m").date()
            except ValueError:
                messages.error(request, "Invalid month format.")
                return redirect('add_monthly_income')

            # Create or update income for that month
            obj, created = MonthlyIncome.objects.update_or_create(
                user=request.user,
                month=month_date,
                defaults={'income': income}
            )
            messages.success(request, "Monthly income saved successfully.")
            return redirect('home')
    else:
        form = MonthlyIncomeForm()

    return render(request, 'trackerapp/add_income.html', {'form': form})