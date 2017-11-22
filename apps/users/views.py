import json
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.views.generic.base import View
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from .models import UserProfile, EmailVerifyRecode, Banner
from .forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm, UploadImageForm, UpdateEmailForm, UserInfoForm
from utils.email_send import send_register_email
from courses.models import Course
from organizations.models import CourseOrg, Teacher
from operations.models import UserFavorite, UserCourse, UserMessage
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from utils.mixin_utils import LoginRequiredMixin


class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class IndexView(View):
    def get(self, request):
        all_banners = Banner.objects.all().order_by('index')[:5]

        courses = Course.objects.all().order_by('-click_nums')
        courses1 = courses[:2]
        courses2 = courses[2:8]

        orgs = CourseOrg.objects.all().order_by('-click_nums')[:15]

        context = {'all_banners': all_banners, 'courses1': courses1, 'courses2': courses2, 'orgs': orgs}
        return render(request, 'index.html', context)


# 激活页面
class ActiveUserView(View):
    def get(self, request, active_code):
        all_records = EmailVerifyRecode.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return render(request, 'users/active_fail.html')
        return redirect('/login/')


# 注册页面
class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, 'users/register.html', {'register_form': register_form})

    def post(self, request):
        # 验证码会自动进行验证
        # 验证数据格式
        # 保存数据进数据库
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get('email', '')
            if UserProfile.objects.filter(email=user_name):
                return render(request, 'users/login.html', {'register_form': register_form, "msg": '用户已存在'})
            pass_word = request.POST.get('password', '')   # 明文

            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.password = make_password(pass_word)
            user_profile.is_active = False
            user_profile.save()

            # 发送消息
            user_message = UserMessage()
            user_message.user = user_profile.id
            user_message.message = "welcome to China"
            user_message.save()

            send_register_email(user_name, 'register')
            return redirect('/login/')
        else:
            return render(request, 'users/register.html', {'register_form': register_form})


# 登录页面
class LoginView(View):
    def get(self, request):
        return render(request, 'users/login.html')

    def post(self, request):
        login_form = LoginForm(request.POST)
        # print(login_form)
        #  对登录的名字,密码进行格式确认
        if login_form.is_valid():
            user_name = request.POST.get('username', '')
            pass_word = request.POST.get('password', '')
            user = authenticate(username=user_name, password=pass_word)
            # print(user)     zhang
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('index'))
                else:
                    return render(request, 'users/login.html', {"msg": '用户未激活'})
            else:
                return render(request, 'users/login.html', {"msg": '用户名或密码错误'})
        return render(request, 'users/login.html', {'login_form': login_form})


# def user_login(request):
#     if request.method == 'POST':
#         user_name = request.POST.get('username', '')
#         pass_word = request.POST.get('password', '')
#         user = authenticate(username=user_name, password=pass_word)
#         # print(user)     zhang
#         if user is not None:
#             login(request, user)
#             context = {}
#             return redirect('/')
#         return render(request, 'users/login.html', {"msg": '用户名或密码错误'})
#     elif request.method == 'GET':
#         return render(request, 'users/login.html')


# 退出登录
class LogoutView(View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect(reverse('index'))


# 忘记密码
class ForgetPwdView(View):
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, 'users/forgetpwd.html', {'forget_form': forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get('email', '')
            send_register_email(email, 'forget')
            return render(request, 'users/send_success.html')
        else:
            return render(request, 'users/forgetpwd.html', {'forget_form': forget_form})


# 重置密码主页面
class ResetView(View):
    def get(self, request, reset_code):
        all_records = EmailVerifyRecode.objects.filter(code=reset_code)
        if all_records:
            for record in all_records:
                email = record.email
                return render(request, 'users/password_reset.html', {'email': email})
        else:
            return render(request, 'users/active_fail.html')


# 重置密码操作页
class ModifyPwdView(View):
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            email = request.POST.get('email', '')
            if pwd1 != pwd2:
                return render(request, 'users/password_reset.html', {'email': email, 'msg': '密码不一致'})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd1)
            user.save()
            return redirect('/login/')
        else:
            email = request.POST.get('email', '')
            return render(request, 'users/password_reset.html', {'email': email, 'modify_form': modify_form})


# 个人资料
class UserInfoView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        # context = {'user': user}
        return render(request, 'usercenter/usercenter-info.html')

    def post(self, request):
        user_form = UserInfoForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            return HttpResponse("{'status': 'success'}", content_type='application/json')
        else:
            return HttpResponse(json.dumps(user_form.errors), content_type='application/json')


# 头像修改
class UploadImageView(LoginRequiredMixin, View):
    def post(self, request):
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            # image = image_form.cleaned_data['image']
            # request.user.image = image
            # request.user.save()
            image_form.save()
            return HttpResponse("{'status': 'success'}", content_type='application/json')
        return HttpResponse("{'status': 'fail'}", content_type='application/json')


# 修改密码
class UpdatePwdView(LoginRequiredMixin, View):
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            password1 = request.POST.get('password1', '')
            password2 = request.POST.get('password2', '')
            if password1 != password2:
                return HttpResponse("{'status': 'fail', 'msg': '密码不一致'}", content_type='application/json')
            request.user.password = make_password(password1)
            request.user.save()
        return HttpResponse("{'status': 'success', 'msg': 'success'}", content_type='application/json')


# 修改邮箱发送验证码   问题:为什么地址是一大长串
class SendEmailCodeView(LoginRequiredMixin, View):
    def get(self, request):
        # 找到邮箱地址
        email = request.user.email
        email = request.GET.get('email','')
        if UserProfile.objects.filter(email=email):
            return HttpResponse("{'status': 'fail', 'msg': 'email is having'}", content_type='application/json')
        # 发送验证码邮件,同时将此验证码保存在EmailVerifyRecode表中
        send_register_email(email, 'update', 6)
        return HttpResponse("{'status': 'success', 'msg': 'success'}", content_type='application/json')


# 修改邮箱
class UpdateEmailView(LoginRequiredMixin, View):
    def post(self, request):
        # form验证格式是否正确
        # 确认验证码
        # 修改邮箱
        email_form = UpdateEmailForm(request.POST)
        if email_form.is_valid():
            email = request.POST.get('email', '')
            code = request.POST.get('code', '')

            email_records = EmailVerifyRecode.objects.filter(email=email, send_type='update')

            if email_records:
                email_record = email_records.order_by('-send_time')[0]
                if email_record.code == code:
                    request.user.email = email
                    request.user.save()
                    return HttpResponse("{'status': 'success', 'msg': 'success'}", content_type='application/json')
                else:
                    return HttpResponse("{'status': 'fail', 'msg': 'code is wrong1'}", content_type='application/json')
            else:
                return HttpResponse("{'status': 'fail', 'msg': 'code is wrong2'}", content_type='application/json')
        return HttpResponse("{'status': 'fail', 'msg': 'code is wrong'}", content_type='application/json')


# 我的课程
class UserCourseView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user

        all_usercourse = UserCourse.objects.filter(user=user)

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_usercourse, 4, request=request)
        all_usercourse = p.page(page)

        context = {'user': user, 'all_usercourse': all_usercourse}
        return render(request, 'usercenter/usercenter-mycourse.html', context)


# 我的消息
class UserMessageView(View):
    def get(self, request):
        user = request.user
        all_usermessages = UserMessage.objects.filter(user=int(user.id))

        all_unread_messages = all_usermessages.filter(has_read=False)
        for unread_message in all_unread_messages:
            unread_message.has_read = True
            unread_message.save()

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_usermessages, 4, request=request)
        all_usermessages = p.page(page)

        context = {'user': user, 'all_usermessages': all_usermessages}
        return render(request, 'usercenter/usercenter-message.html', context)


# 我的收藏 课程机构
class UserFavOrgView(View):
    def get(self, request):
        user = request.user

        user_fav_orgs = UserFavorite.objects.filter(user=user, fav_type=2)

        org_list = []
        for org in user_fav_orgs:
            course_org = CourseOrg.objects.filter(id=org.fav_id)
            if course_org:
                org_list.append(course_org[0])

        context = {'user': user, 'org_list': org_list}
        return render(request, 'usercenter/usercenter-fav-org.html', context)


# 我的收藏 授课教师
class UserFavTeacherView(View):
    def get(self, request):
        user = request.user

        user_fav_teachers = UserFavorite.objects.filter(user=user, fav_type=3)

        teacher_list = []
        for teacher in user_fav_teachers:
            course_org = Teacher.objects.filter(id=teacher.fav_id)
            if course_org:
                teacher_list.append(course_org[0])

        context = {'user': user, 'teacher_list': teacher_list}
        return render(request, 'usercenter/usercenter-fav-teacher.html', context)


# 我的收藏 公开课程
class UserFavCourseView(View):
    def get(self, request):
        user = request.user

        user_fav_courses = UserFavorite.objects.filter(user=user, fav_type=1)
        print(user_fav_courses)
        course_list = []
        for course in user_fav_courses:
            course_org = Course.objects.filter(id=course.fav_id)
            if course_org:
                course_list.append(course_org[0])

        context = {'user': user, 'course_list': course_list}
        return render(request, 'usercenter/usercenter-fav-course.html', context)


def page_not_found(request):
    response = render_to_response('status/404.html')
    response.status_code = 404
    return response


def server_error(request):
    response = render_to_response('status/500.html', {})
    response.status_code = 500
    return response

