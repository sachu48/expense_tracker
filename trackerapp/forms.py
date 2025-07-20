from django import forms
from .models import Expense
from .models import MonthlyIncome

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['title', 'amount', 'category', 'date']

class MonthlyIncomeForm(forms.ModelForm):
    month = forms.CharField(widget=forms.TextInput(attrs={'type': 'month'}))

    class Meta:
        model = MonthlyIncome
        fields = ['income', 'month']
