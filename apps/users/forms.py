from django import forms
from captcha.fields import CaptchaField
from .models import UserProfile


class LoginForm(forms.Form):
    username = forms.CharField(required=True, min_length=3)
    password = forms.CharField(required=True, max_length=20, min_length=5)


class RegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, max_length=20, min_length=5)
    captcha = CaptchaField(error_messages={'invaild': '验证码错误'})


class ForgetForm(forms.Form):
    email = forms.EmailField(required=True)
    captcha = CaptchaField(error_messages={'invaild': '验证码错误'})


class ModifyPwdForm(forms.Form):
    password1 = forms.CharField(required=True, max_length=20, min_length=5)
    password2 = forms.CharField(required=True, max_length=20, min_length=5)


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']


class UpdateEmailForm(forms.Form):
    email = forms.EmailField(required=True)
    code = forms.CharField(required=True)


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['nick_name', 'birthday', 'gender', 'address', 'mobile', 'email']
