from django import forms
from .models import ManufacturingGoal

class GoalsForm(forms.Form):
	name = forms.CharField(label='Goal Name', max_length=500, required=True)

class GoalsChoiceForm(forms.Form):
	goal = forms.ModelChoiceField(queryset=ManufacturingGoal.objects.filter(user=self.user))

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', None)
		super(GoalsChoiceForm, self).__init__(*args, **kwargs)
