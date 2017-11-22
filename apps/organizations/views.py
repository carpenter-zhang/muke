from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import HttpResponse
from django.db.models import Q

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from .models import *
from courses.models import Course
from operations.models import UserFavorite, UserMessage
from .forms import UserAskForm


class OrgListView(View):
    def get(self, request):
        # print(request)  /org/?ct=pxjg
        all_orgs = CourseOrg.objects.all()
        all_citys = CityDict.objects.all()

        # 授课机构排名
        hot_orgs = all_orgs.order_by('-click_nums')[:3]

        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_orgs = all_orgs.filter(Q(name__contains=search_keywords)|Q(desc__contains=search_keywords))

        # 城市的筛选
        city_id = request.GET.get('city', '')
        if city_id:
            all_orgs = all_orgs.filter(city_id=int(city_id))

        category = request.GET.get('ct', '')
        if category:
            all_orgs = all_orgs.filter(category=category)

        # 通过学习人数进行排序
        sort = request.GET.get('sort', '')
        if sort == 'students':
            all_orgs = all_orgs.order_by('-students')
        if sort == 'courses':
            all_orgs = all_orgs.order_by('-course_nums')

        org_nums = all_orgs.count()
        # 对课程机构进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(all_orgs, 5, request=request)

        orgs = p.page(page)

        context = {'all_orgs': orgs,
                   'all_citys': all_citys,
                   'org_nums': org_nums,
                   'city_id': city_id,
                   'category': category,
                   'hot_orgs': hot_orgs,
                   'sort': sort}
        return render(request, 'orgs/org-list.html', context)


# 用户咨询学习
class AddUserAskView(View):
    def post(self, request):
        userask_form = UserAskForm(request.POST)
        if userask_form.is_valid():
            user_ask = userask_form.save(commit=True)
            # 前面是form验证,成功后直接将数据存到数据库中,此时在后台就已经完成了操作,
            # 接下来就是在前台通过ajax技术,完成前端的交互.
            return HttpResponse("{'status': 'success'}", content_type='application/json')
        else:
            return HttpResponse("{'status': 'fail', 'msg': 'error message'}", content_type='application/json')


# 机构首页
class OrgHomeView(View):
    def get(self, request, org_id):
        course_org = CourseOrg.objects.get(id=int(org_id))
        # all_courses = Course.objects.filter(course_org=course_org).order_by('-add_time')[:3]
        # teacher = Teacher.objects.filter(org=course_org)[0]
        all_courses = course_org.course_set.all()[:3]
        # 必须有教师,否则空列表报错
        # teacher = course_org.teacher_set.all()[0]
        teacher = []
        teacher1 = course_org.course_set.all()
        if teacher1:
            teacher = teacher1[0]

        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(course_org.id), fav_type=2):
                has_fav = True

        course_org.click_nums += 1
        course_org.save()

        context = {'course_org': course_org, 'all_courses': all_courses, 'teacher': teacher, 'has_fav': has_fav, 'page': 'home'}
        return render(request, 'orgs/org-detail-homepage.html', context)


# 机构课程页
class OrgCourseView(View):
    def get(self, request, org_id):
        course_org = CourseOrg.objects.get(id=int(org_id))
        # course_org = CourseOrg.objects.filter(id=int(org_id))
        # print(course_org)
        # course_org = course_org[0]

        # get方法     CourseOrg object  ,如果model有__str__方法,则返回该方法的返回值: 济南大学
        # filter方法  [<CourseOrg: CourseOrg object>] 如果model有__str__方法,则返回 [<CourseOrg: 济南大学>]

        courses = course_org.course_set.all()
        # if courses:
        #     if len(courses) > 5:
        #         courses = courses.order_by('-fav_nums')[:5]
        #     else:
        #         courses = courses.order_by('-fav_nums')
        # else:
        #     courses = []

        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(course_org.id), fav_type=2):
                has_fav = True

        context = {'course_org': course_org, 'courses': courses, 'has_fav': has_fav, 'page': 'course'}
        return render(request, 'orgs/org-detail-course.html', context)


# 机构介绍页
class OrgDescView(View):
    def get(self, request, org_id):
        course_org = CourseOrg.objects.get(id=int(org_id))

        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(course_org.id), fav_type=2):
                has_fav = True

        context = {'course_org': course_org, 'has_fav': has_fav, 'page': 'desc'}
        return render(request, 'orgs/org-detail-desc.html', context)


# 机构教师页
class OrgTeacherView(View):
    def get(self, request, org_id):
        course_org = CourseOrg.objects.get(id=int(org_id))
        all_teachers = course_org.teacher_set.all()
        has_fav = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(course_org.id), fav_type=2):
                has_fav = True

        context = {'course_org': course_org, 'all_teachers': all_teachers, 'has_fav': has_fav, 'page': 'teacher'}
        return render(request, 'orgs/org-detail-teachers.html', context)


# 用户的机构收藏
class AddFavView(View):
    def post(self, request):
        fav_id = request.POST.get('fav_id', 0)
        fav_type = request.POST.get('fav_type', 0)

        # 判断用户是否登录
        if not request.user.is_authenticated():
            return HttpResponse("{'status': 'fail', 'msg': '用户未登录'}", content_type='application/json')

        # 查找用户是否已经收藏
        exist_records = UserFavorite.objects.filter(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
        if exist_records:
            # 取消收藏
            exist_records.delete()
            if int(fav_type) == 1:
                course = Course.objects.get(id=int(fav_id))
                course.fav_nums -= 1
                if course.fav_nums < 0:
                    course.fav_nums = 0
                course.save()
            elif int(fav_type) == 2:
                course_org = CourseOrg.objects.get(id=int(fav_id))
                course_org.fav_nums -= 1
                if course_org.fav_nums < 0:
                    course_org.fav_nums = 0
                course_org.save()
            elif int(fav_type) == 3:
                teacher = Teacher.objects.get(id=int(fav_id))
                teacher.fav_nums -= 1
                if teacher.fav_nums < 0:
                    teacher.fav_nums = 0
                teacher.save()
            return HttpResponse("{'status': 'success', 'msg': '用户已取消收藏'}", content_type='application/json')
        else:
            user_fav = UserFavorite()
            if int(fav_id) > 0 and int(fav_type) > 0:
                user_fav.user = request.user
                user_fav.fav_id = int(fav_id)
                user_fav.fav_type = int(fav_type)
                user_fav.save()

                if int(fav_type) == 1:
                    course = Course.objects.get(id=int(fav_id))
                    course.fav_nums += 1
                    course.save()
                elif int(fav_type) == 2:
                    course_org = CourseOrg.objects.get(id=int(fav_id))
                    course_org.fav_nums += 1
                    course_org.save()
                elif int(fav_type) == 3:
                    teacher = Teacher.objects.get(id=int(fav_id))
                    teacher.fav_nums += 1
                    teacher.save()

                # 发送消息
                user_message = UserMessage()
                user_message.user = request.user
                user_message.message = "welcome to China"
                user_message.save()
                return HttpResponse("{'status': 'success', 'msg': '用户已收藏'}", content_type='application/json')
            else:
                return HttpResponse("{'status': 'fail', 'msg': '收藏出错'}", content_type='application/json')


# 教师列表页
class TeacherListView(View):
    def get(self, request):
        all_teachers = Teacher.objects.all()

        keywords = request.GET.get('keywords', '')
        if keywords:
            all_teachers = all_teachers.filter(Q(name__contains=keywords)|Q(work_company__contains=keywords))

        sort = request.GET.get('sort', '')
        if sort == 'hot':
            all_teachers = all_teachers.order_by('-click_nums')

        teacher_nums = all_teachers.count()

        teacher_order = all_teachers.order_by('-fav_nums')[:3]

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_teachers, 4, request=request)
        # 传到网页的是这个教师列表
        all_teachers = p.page(page)

        context = {'all_teachers': all_teachers, 'sort': sort, 'teacher_nums': teacher_nums,
                   'teacher_order': teacher_order}
        return render(request, 'teachers/teachers-list.html', context)


# 教师详情页
class TeacherDetailView(View):
    def get(self, request, teacher_id):
        teacher = Teacher.objects.get(id=int(teacher_id))

        courses = teacher.course_set.all().order_by('-click_nums')
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(courses, 2, request=request)
        courses = p.page(page)

        org = teacher.org

        teacher_order = Teacher.objects.all().order_by('-fav_nums')[:3]

        has_fav_teacher = False
        has_fav_org = False

        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(teacher_id), fav_type=3):
                has_fav_teacher = True
            if UserFavorite.objects.filter(user=request.user, fav_id=int(teacher.org.id), fav_type=2):
                has_fav_org = True

        teacher.click_nums += 1
        teacher.save()
        context = {'teacher': teacher, 'courses': courses, 'org': org, 'teacher_order': teacher_order,
                   'has_fav_teacher': has_fav_teacher, 'has_fav_org': has_fav_org}
        return render(request, 'teachers/teacher-detail.html', context)
