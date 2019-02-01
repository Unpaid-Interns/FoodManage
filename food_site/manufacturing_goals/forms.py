from django import forms
from .models import ManufacturingGoal

class GoalsForm(forms.Form):
	name = forms.CharField(label='Goal Name', max_length=500, required=True)

class GoalsChoiceForm(forms.Form):
	goal = forms.ModelChoiceField(queryset=ManufacturingGoal.objects.all())

	def __init__(self, *args, **kwargs):
		this_user = kwargs.pop('user', None)
		super(GoalsChoiceForm, self).__init__(*args, **kwargs)
		
		if this_user:
			self.fields['goal'].queryset = ManufacturingGoal.objects.filter(user=this_user)
