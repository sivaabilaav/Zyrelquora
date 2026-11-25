
from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ['rating', 'comment']

        widgets = {
            'rating': forms.Select(
                choices=[
                    (5, '★★★★★ - Excellent'),
                    (4, '★★★★ - Very Good'),
                    (3, '★★★ - Good'),
                    (2, '★★ - Fair'),
                    (1, '★ - Poor'),
                ],
                attrs={'class': 'form-select'}
            ),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your review...',
                'rows': 4
            }),
        }
