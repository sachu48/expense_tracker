from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Expense
from .forms import ExpenseForm
from django import forms

def home(request):
    return render(request, 'trackerapp/home.html')

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

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'date', 'description']

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            return redirect('expense_list')  # redirect to the list after saving
    else:
        form = ExpenseForm()
    return render(request, 'trackerapp/add_expense.html', {'form': form})

from .models import Expense

@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user).order_by('-date')
    return render(request, 'trackerapp/expense_list.html', {'expenses': expenses})
# trackerapp/views.py
def view_expenses(request):
    return render(request, 'trackerapp/view_expenses.html')

