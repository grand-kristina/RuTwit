from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.http import HttpResponseRedirect

from .forms import CreationForm
from .models import UserProfile


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy("login")
    template_name = "users/signup.html"
    
    def form_valid(self, form):
        self.object = form.save()
        UserProfile.objects.create(user=self.object)

        return HttpResponseRedirect(self.get_success_url())

    
