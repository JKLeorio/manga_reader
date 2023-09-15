
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import UpdateView

from users.forms import RegisterForm, UserUpdateForm
from users.models import User


class RegisterView(View):
    template_name = 'registration/register.html'

    def get(self, request):
        context = {
            'form': RegisterForm()
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = RegisterForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=password)
            login(request, user)
            return redirect('manga_list')
        context = {
            'form': form
        }
        return render(request, self.template_name, context)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'profile_update.html'
    queryset = User.objects.all()

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('user_profile_update', kwargs={'pk': self.request.user.pk})