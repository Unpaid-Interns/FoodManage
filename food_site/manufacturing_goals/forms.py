from django import forms
from .models import ManufacturingGoal
import datetime

class GoalsForm(forms.Form):
	name = forms.CharField(label='Goal Name', max_length=500, required=True)
	deadline = forms.DateField(initial=datetime.date.today)

class ManufacturingSchedForm(forms.Form):
	data = forms.CharField(label='Data', required=True)
	overrides = forms.CharField(label='Overrides', required=True)
