from django import forms


class MyForm(forms.Form):
    # the default format is %Y-%m-%d
    date_available = forms.DateField(
        widget=forms.widgets.DateInput(format="%d/%m/%Y"))