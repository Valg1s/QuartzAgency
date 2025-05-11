import sys
from pathlib import Path
from functools import wraps

from django.views import View
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from .models import CustomUser, ProfileType
from .forms import RegistrationUserForm, AdditionalRegistrationForm, LoginUserForm

sys.path.append(str(Path(__file__).parent.parent))

try:
    from app.utils import init_logger
except ImportError as e:
    exit(f"Views:: Cannot import init_logger {e}")

LoginRequiredMixin.login_url = 'app:login'

class BaseView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.logger = init_logger(file_log=False)
        self.logging_header = f"{self.__class__.__name__}:: "

    def exception(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            try:
                self.logger.info(f"{self.logging_header}User data:: {args} :: {kwargs}")

                result = method(self,*args,**kwargs)

                self.logger.info(f"Server response:: {result}")

                return result

            except Exception as e:
                self.logger.error(f"{self.logging_header}Exception: {e}")
                return HttpResponse(str(e), content_type="text/plain", status=500)

        return wrapper

class SessionStatusView(BaseView):
    @BaseView.exception
    def get(self, request):
        if request.user.is_authenticated:
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'status': 'unauthorized'}, status=401)

class LoginView(BaseView):
    @BaseView.exception
    def get(self, request):
        return render(request, 'auth/login.html')

    @BaseView.exception
    def post(self, request):
        form = LoginUserForm(request.POST)
        if not form.is_valid():
            self.logger.error(f"LoginForm:: Error: {form.errors}")
            return JsonResponse(form.errors, status=400)

        username = form.cleaned_data['username']
        password = form.cleaned_data['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            self.logger.info(f"{self.logging_header}User:: {username} successfully logged in")
            return redirect('app:main')

        self.logger.info(f"{self.logging_header}User:: {username} failed to login")
        return HttpResponse(f"{username} failed to login", content_type="text/plain", status=403)

class RegisterView(BaseView):
    @BaseView.exception
    def get(self, request):
        return render(request, 'auth/register.html')

    @BaseView.exception
    def post(self, request):
        form = RegistrationUserForm(request.POST)

        if not form.is_valid():
            return JsonResponse(form.errors, status=400)

        email = request.POST['email']
        contact = request.POST['contact']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        profile_type = request.POST['profile_type']

        if password != confirm_password:
            response = HttpResponse(f"{email} passwords do not match", status=403)
            return response

        request.session['register_data'] = {
            'email': email,
            'contact': contact,
            'password': password,
            'profile_type': profile_type
        }

        return redirect('app:data_form')

class RegisterDataView(BaseView):
    @BaseView.exception
    def get(self, request):
        user_type = request.session.get('register_data', {}).get('profile_type')

        if not user_type:
            self.logger.error(f"{self.logging_header} Unexpected error. User comes on data form without registration")
            return redirect('app:register')

        if user_type == ProfileType.EMPLOYEE:
            return render(request, "auth/employer_register.html")
        elif user_type == ProfileType.COMPANY:
            return render(request, "auth/company_register.html")
        else:
            self.logger.error(f"{self.logging_header} Unexpected error. Unknown user type: {user_type}")
            return HttpResponse(f"{user_type} unknown user type", content_type="text/plain", status=404)

    @BaseView.exception
    def post(self, request):
        prev_register_data = request.session.get('register_data', {})

        if not prev_register_data:
            self.logger.error(f"{self.logging_header} Unexpected error. User comes on data form without registration")
            return redirect('app:register')

        form = AdditionalRegistrationForm(request.POST)

        if not form.is_valid():
            self.logger.error(f"{self.logging_header} Unexpected error. Error on form {form.errors}")
            return JsonResponse(form.errors, status=400)

        try:
            result = CustomUser.objects.create_user(**prev_register_data,**form.cleaned_data)
        except Exception as e:
            self.logger.error(f"{self.logging_header}Exception: {e} on creating new user")
            return HttpResponse(str(e), content_type="text/plain", status=500)

        self.logger.info(f"{self.logging_header}User:: {result} successfully registered")

        request.session['register_data'] = {}
        return redirect('app:login')

class LogoutView(LoginRequiredMixin, BaseView):
    @BaseView.exception
    def post(self, request):
        logout(request)

        return redirect("app:login")


class MainView(LoginRequiredMixin, BaseView):
    @BaseView.exception
    def get(self, request):
        return render(request, "main.html")


