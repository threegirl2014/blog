from django import forms


class ContactForm(forms.Form):
    subject = forms.CharField(label='Subject:', max_length=100)
    message = forms.CharField(label = 'Message:', widget=forms.Textarea)
    email = forms.EmailField(label='E-mail:')
    name = forms.CharField(label='Name:',max_length=50,required=False)
#     cc_myself = forms.BooleanField(required=False)