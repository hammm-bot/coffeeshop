from django import forms
from .models import TransaksiManual

class BuktiPembayaranForm(forms.ModelForm):
    class Meta:
        model = TransaksiManual
        fields = ['bukti_pembayaran']
