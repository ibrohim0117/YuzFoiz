from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User
from .validators import MAX_IMAGE_SIZE_MB


class RegisterForm(UserCreationForm):
    """Ism, familiya, username va parol — hammasi majburiy."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username')
        labels = {
            'first_name': 'Ism',
            'last_name': 'Familiya',
            'username': 'Username',
        }
        help_texts = {
            'username': "150 belgigacha: harflar, raqamlar va @ . + - _ belgilari.",
        }
        error_messages = {
            'username': {
                'unique': "Bu username band. Boshqasini tanlang.",
                'invalid': "Username faqat harflar, raqamlar va @ . + - _ belgilaridan iborat bo'lishi mumkin.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Modelda ism/familiya ixtiyoriy, ro'yxatdan o'tishda esa majburiy
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

        self.fields['username'].widget.attrs.pop('autofocus', None)
        self.fields['first_name'].widget.attrs['autofocus'] = True

        self.fields['password1'].label = 'Parol'
        self.fields['password2'].label = 'Parolni takrorlang'
        self.fields['password2'].help_text = 'Tekshirish uchun parolni qayta kiriting.'


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Username'
        self.fields['password'].label = 'Parol'


class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('image',)
        labels = {'image': 'Rasm'}
        widgets = {'image': forms.FileInput(attrs={'accept': 'image/*'})}
        error_messages = {'image': {'required': 'Rasm tanlang.'}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = True
        self.fields['image'].help_text = f'Maksimal hajm: {MAX_IMAGE_SIZE_MB} MB.'

    def clean_image(self):
        # Bekor qilingan rasm bo'lsa, FileField fayl tanlanmasa ham eski rasmni qaytaradi.
        # Bizga aynan yangi fayl kerak.
        if not self.files.get('image'):
            raise forms.ValidationError('Rasm tanlang.')
        return self.cleaned_data['image']
