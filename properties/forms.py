import re
from django import forms
from django.core.exceptions import ValidationError
from .models import Property, Deal, Review, Client


class PropertyFilterForm(forms.Form):
    search = forms.CharField(required=False, label='Поиск', widget=forms.TextInput(attrs={'placeholder': 'Адрес, название...', 'class': 'form-control'}))
    category = forms.IntegerField(required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    transaction_type = forms.ChoiceField(required=False, choices=[('', 'Все'), ('sale', 'Продажа'), ('rent', 'Аренда')], widget=forms.Select(attrs={'class': 'form-select'}))
    price_min = forms.DecimalField(required=False, label='Цена от', widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'}))
    price_max = forms.DecimalField(required=False, label='Цена до', widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '999999'}))
    city = forms.CharField(required=False, label='Город', widget=forms.TextInput(attrs={'class': 'form-control'}))
    rooms = forms.IntegerField(required=False, label='Комнат', widget=forms.NumberInput(attrs={'class': 'form-control'}))
    sort = forms.ChoiceField(required=False, choices=[
        ('', 'По умолчанию'), ('price', 'Цена ↑'), ('-price', 'Цена ↓'),
        ('area', 'Площадь ↑'), ('-area', 'Площадь ↓'), ('-created_at', 'Сначала новые'),
    ], widget=forms.Select(attrs={'class': 'form-select'}))


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        exclude = ['views_count', 'created_at', 'updated_at']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'tags': forms.CheckboxSelectMultiple(),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise ValidationError('Цена не может быть отрицательной.')
        return price

    def clean_area(self):
        area = self.cleaned_data.get('area')
        if area is not None and area <= 0:
            raise ValidationError('Площадь должна быть больше 0.')
        return area


class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
        exclude = ['created_at', 'updated_at']
        widgets = {
            'contract_date': forms.DateInput(attrs={'type': 'date'}),
            'sale_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        sale_date = cleaned_data.get('sale_date')
        end_date = cleaned_data.get('end_date')
        contract_date = cleaned_data.get('contract_date')
        deal_type = cleaned_data.get('deal_type')
        if sale_date and contract_date and sale_date < contract_date:
            raise ValidationError('Дата продажи не может быть раньше даты договора.')
        if deal_type == 'rent' and end_date and sale_date and end_date < sale_date:
            raise ValidationError('Дата окончания аренды должна быть позже даты начала.')
        return cleaned_data


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'rating', 'text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'rating': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_text(self):
        text = self.cleaned_data.get('text', '')
        if len(text) < 10:
            raise ValidationError('Отзыв должен содержать не менее 10 символов.')
        return text


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ['user', 'created_at', 'updated_at']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        pattern = r'^\+375 \((29|33|44|25)\) \d{3}-\d{2}-\d{2}$'
        if phone and not re.match(pattern, phone):
            raise ValidationError('Формат: +375 (29) XXX-XX-XX')
        return phone
