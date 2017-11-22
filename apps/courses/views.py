from django.shortcuts import render, redirect
from django.views .generic import View
from django.http import HttpResponse
from django.db.models import Q

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from .models import *
from operations.models import *
from utils.mixin_utils import LoginRequiredMixin


# 课程列表页
class CourseListView(View):
    def get(self, request):
        all_courses = Course.objects.all()

        hot_courses = all_courses.order_by('-click_nums')[:3]

        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_courses = all_courses.filter(Q(name__icontains=search_keywords)|Q(desc__icontains=search_keywords)|Q(detail__icontains=search_keywords))

        sort = request.GET.get('sort', '')
        if sort == 'hot':
            all_courses = all_courses.order_by('-fav_nums')
        elif sort == 'students':
            all_courses = all_courses.order_by('-students')
        else:
            all_courses = all_courses.order_by('-add_time')
            sort = ''

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_courses, 6, request=request)
        courses = p.page(page)

        context = {'all_courses': courses, 'hot_courses': hot_courses, 'sort': sort}
        return render(request, 'courses/course-list.html', context)


# 课程详情页
class CourseDetailView(View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))

        course.click_nums += 1
        course.save()

        org = course.course_org
        #  可以直接在html中使用 course.course_org  效果和这个一样

        tag = course.tag
        relate_courses = []
        if tag:
            relate_courses = Course.objects.filter(tag=tag)[:1]

            if course.id == relate_courses[0].id:
                relate_courses = Course.objects.filter(tag=tag)[1:2]

        has_fav_1 = False
        has_fav_2 = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(course.id), fav_type=1):
                has_fav_1 = True
            if UserFavorite.objects.filter(user=request.user, fav_id=int(org.id), fav_type=2):
                has_fav_2 = True

        context = {'course': course, 'relate_courses': relate_courses, 'org': org, 'has_fav_1': has_fav_1,
                   'has_fav_2': has_fav_2}
        return render(request, 'courses/course-detail.html', context)


# 课程学习页
class CourseVideoView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        lessons = course.lesson_set.all()
        resources = CourseResource.objects.filter(course=course)

        course.students += 1
        course.save()

        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        # 符合用户课程表的数据,也就是所有学习这门课程的所有学生
        user_courses = UserCourse.objects.filter(course=course)
        # 所有学生的id
        user_ids = [user_course.user.id for user_course in user_courses]
        # 所有学生学习的课程id
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [user_course.course.id for user_course in all_user_courses]

        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]

        context = {'course': course, 'lessons': lessons, 'resources': resources, 'relate_courses': relate_courses}
        return render(request, 'courses/course-video.html', context)


# 课程评论页
class CourseCommentView(LoginRequiredMixin, View):
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        lessons = course.lesson_set.all()
        resources = CourseResource.objects.filter(course=course)

        all_comments = CourseComment.objects.filter(course=course).order_by('-add_time')
        if len(all_comments) > 10:
            all_comments = all_comments[:10]

        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [user_course.course.id for user_course in all_user_courses]
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]

        context = {'course': course, 'lessons': lessons, 'resources': resources, 'all_comments': all_comments, 'relate_courses': relate_courses}
        return render(request, 'courses/course-comment.html', context)


# 添加评论
class AddCommentView(View):
    def post(self, request):
        if not request.user.is_authenticated():
            # return HttpResponse("{'status': 'fail', 'msg': '用户未登录'}", content_type='application/json')
            return redirect('/login/')

        course_id = request.POST.get('course_id', 0)
        comments = request.POST.get('comment', '')

        if int(course_id) > 0 and comments:
            course_comment = CourseComment()
            course = Course.objects.get(id=int(course_id))
            course_comment.course = course
            course_comment.comments = comments
            course_comment.user = request.user
            course_comment.save()
            # return HttpResponse("{'status': 'success', 'msg': '评论成功'}", content_type='application/json')

        course = Course.objects.get(id=int(course_id))
        lessons = course.lesson_set.all()
        resources = CourseResource.objects.filter(course=course)

        all_comments = CourseComment.objects.filter(course=course).order_by('-add_time')
        if len(all_comments) > 10:
            all_comments = all_comments[:10]

        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [user_course.course.id for user_course in all_user_courses]
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]

        context = {'course': course, 'lessons': lessons, 'resources': resources, 'all_comments': all_comments, 'relate_courses': relate_courses}
        return render(request, 'courses/course-comment.html', context)


class CoursePlayView(View):
    def get(self, request, video_id):
        video = Video.objects.get(id=int(video_id))
        course = video.lesson.course
        lessons = course.lesson_set.all()
        resources = CourseResource.objects.filter(course=course)

        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        if not user_courses:
            user_course = UserCourse(user=request.user, course=course)
            user_course.save()

        # 符合用户课程表的数据,也就是所有学习这门课程的所有学生
        user_courses = UserCourse.objects.filter(course=course)
        # 所有学生的id
        user_ids = [user_course.user.id for user_course in user_courses]
        # 所有学生学习的课程id
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        course_ids = [user_course.course.id for user_course in all_user_courses]

        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]

        context = {'video': video, 'course': course, 'lessons': lessons,
                   'resources': resources, 'relate_courses': relate_courses}
        return render(request, 'courses/course-play.html', context)
