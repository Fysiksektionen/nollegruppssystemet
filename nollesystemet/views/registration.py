from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView

import nollesystemet.models as models
import nollesystemet.forms as forms
import nollesystemet.mixins as mixins


class RegistrationView(mixins.FadderietMixin, UpdateView):
    model = models.Registration
    form_class = forms.RegistrationForm
    template_name = 'fadderiet/evenemang/anmalan.html'

    success_url = reverse_lazy('fadderiet:evenemang:index')

    login_required = True

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            self.happening = models.Happening.objects.get(pk=self.kwargs['pk'])
        except models.Happening.DoesNotExist:
            self.happening = None
        else:
            try:
                self.registration = models.Registration.objects.get(user=self.request.user.profile, happening=self.happening)
            except:
                if self.happening is None:
                    self.raise_exception = True
                    self.handle_no_permission()
                else:
                    self.registration = None
        self.registration_user = self.request.user.profile
        self.observing_user = self.request.user.profile

    def test_func(self):
        if self.registration:
            return self.registration.can_see(self.observing_user)
        else:
            return self.happening.can_register(self.observing_user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.registration is None:
            kwargs.update({
                'happening': self.happening,
                'user': self.registration_user,
            })
        else:
            kwargs.update({
                'editable': False
            })
        kwargs.update({
            'observing_user': self.observing_user,
        })
        return kwargs

    def get_initial(self):
        if self.request.user.profile.food_preference:
            self.initial.update({'food_preference': self.request.user.profile.food_preference})
        return super().get_initial()

    def get_object(self, queryset=None):
        return self.registration

    def get_context_data(self, **kwargs):
        dynamic_extra_context = {
            'happening': self.happening
        }
        kwargs.update(**dynamic_extra_context)
        return super().get_context_data(**kwargs)

class RegistrationUpdateView(mixins.FohserietMixin, UpdateView):
    model = models.Registration
    form_class = forms.RegistrationForm
    template_name = 'fohseriet/anmalan/redigera.html'

    login_required = True

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            self.registration = models.Registration.objects.get(pk=self.kwargs['pk'])
        except models.Registration.DoesNotExist:
            self.raise_exception = True
            self.handle_no_permission()

        self.happening = self.registration.happening
        self.registration_user = self.registration.user
        self.observing_user = self.request.user.profile

        self.default_back_url = reverse('fohseriet:anmalan:visa', kwargs={'pk': self.registration.pk})
        self.success_url = self.default_back_url

    def test_func(self):
        return self.registration.can_edit(self.request.user.profile)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'observing_user': self.observing_user,
            'editable': True,
            'deletable': True
        })
        return kwargs


class RegistrationSeeView(mixins.FohserietMixin, UpdateView):
    model = models.Registration
    form_class = forms.RegistrationForm
    template_name = 'fohseriet/anmalan/visa.html'

    default_back_url = reverse_lazy('foseriet:anvandare:anmalningar')

    login_required = True

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        try:
            self.registration = models.Registration.objects.get(pk=self.kwargs['pk'])
        except models.Registration.DoesNotExist:
            self.raise_exception = True
            self.handle_no_permission()

        self.happening = self.registration.happening
        self.registration_user = self.registration.user
        self.observing_user = self.request.user.profile

        self.success_url = self.back_url

    def test_func(self):
        return self.registration.can_see(self.request.user.profile)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'observing_user': self.observing_user,
            'editable': False
        })
        return kwargs