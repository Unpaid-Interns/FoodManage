from django import forms
from .models import ManufacturingGoal
import datetime

class GoalsForm(forms.Form):
	name = forms.CharField(label='Goal Name', max_length=500, required=True)
	deadline = forms.DateField(initial=datetime.date.today)

class GoalsChoiceForm(forms.Form):
	goal = forms.ModelChoiceField(queryset=ManufacturingGoal.objects.all())

	def __init__(self, *args, **kwargs):
		this_user = kwargs.pop('user', None)
		super(GoalsChoiceForm, self).__init__(*args, **kwargs)
		
		if this_user:
			self.fields['goal'].queryset = ManufacturingGoal.objects.filter(user=this_user)

class ManufacturingSchedForm(forms.Form):
	data = forms.CharField(label='Data', required=True)
