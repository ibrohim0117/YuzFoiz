from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import LoginForm, ProfileImageForm, RegisterForm
from .models import User


class AnonymousRequiredMixin:
    """Login qilgan foydalanuvchi bu sahifaga kirsa, profilga yo'naltiriladi."""

    authenticated_redirect_url = reverse_lazy('accounts:profile')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.authenticated_redirect_url)
        return super().dispatch(request, *args, **kwargs)


class RegisterView(AnonymousRequiredMixin, CreateView):
    form_class = RegisterForm
    template_name = 'register.html'
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(self.request, "Ro'yxatdan muvaffaqiyatli o'tdingiz!")
        return response


class UserLoginView(AnonymousRequiredMixin, LoginView):
    form_class = LoginForm
    template_name = 'login.html'


class UserLogoutView(LogoutView):
    """Faqat POST orqali ishlaydi (Django xavfsizlik talabi)."""

    next_page = reverse_lazy('accounts:login')

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.info(request, 'Tizimdan chiqdingiz.')
        return response


class ProfileView(LoginRequiredMixin, UpdateView):
    form_class = ProfileImageForm
    template_name = 'profile.html'
    success_url = reverse_lazy('accounts:profile')
    # 'user' nomini band qilmaslik uchun: shablonda `user` = request.user bo'lib qoladi
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        # request.user emas, uning alohida nusxasi: forma xato bo'lsa,
        # sahifada ko'rsatiladigan ma'lumot (rasm, holat) buzilmasin
        return User.objects.get(pk=self.request.user.pk)

    def form_valid(self, form):
        messages.success(self.request, "Rasm yuklandi. Admin ko'rib chiqishini kuting.")
        return super().form_valid(form)
