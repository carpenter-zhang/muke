from datetime import datetime

from django.db import models
from organizations.models import CourseOrg, Teacher


# 课程
class Course(models.Model):
    course_org = models.ForeignKey(CourseOrg, verbose_name='课程机构', null=True, blank=True)
    teacher = models.ForeignKey(Teacher, verbose_name='教师', null=True, blank=True)
    name = models.CharField(max_length=20, verbose_name='课程名')
    desc = models.CharField(max_length=500, verbose_name='简介')
    detail = models.TextField(verbose_name='详细信息')
    degree = models.CharField(choices=(('cj', '初级'), ('zj', '中级'), ('gj', '高级')), max_length=10, verbose_name='难度')
    learn_times = models.IntegerField(verbose_name='学习时间', default=0)
    students = models.IntegerField(default=0, verbose_name='学习人数')
    fav_nums = models.IntegerField(default=0, verbose_name='收藏人数')
    image = models.ImageField(upload_to='course/%Y/%m',default='image/default.png', verbose_name='封面')
    click_nums = models.IntegerField(default=0, verbose_name='点击数')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')
    category = models.CharField(max_length=20, verbose_name='课程类别', default='后端开发')
    tag = models.CharField(default='', verbose_name='课程标签', max_length=20)
    need_know = models.CharField(max_length=100, verbose_name='课程须知', default='')
    tea_tell = models.CharField(max_length=300, verbose_name='老师告诉', default='')

    class Meta:
        verbose_name = '课程'
        verbose_name_plural = verbose_name

    # 返回章节课程数
    def get_zj_nums(self):
        all_lessons = self.lesson_set.all().count()
        return all_lessons

    # 返回学习用户
    def get_learn_users(self):
        learn_users = self.usercourse_set.all()
        if len(learn_users) > 5:
            return learn_users[:5]
        return learn_users

    def __str__(self):
        return self.name


# 章
class Lesson(models.Model):
    course = models.ForeignKey(Course, verbose_name='所属课程')
    name = models.CharField(max_length=20, verbose_name='章节名')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '章节'
        verbose_name_plural = verbose_name

    def get_video(self):
        return self.video_set.all()

    def __str__(self):
        return self.name


# 节
class Video(models.Model):
    lesson = models.ForeignKey(Lesson, verbose_name='章节')
    name = models.CharField(max_length=100, verbose_name='视频名')
    url = models.CharField(max_length=500, default='', verbose_name='视频地址')
    video_times = models.IntegerField(verbose_name='视频时间', default=0)
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '视频'
        verbose_name_plural = verbose_name


# 课程资源
class CourseResource(models.Model):
    course = models.ForeignKey(Course, verbose_name='课程')
    name = models.CharField(max_length=100, verbose_name='名称')
    download = models.FileField(upload_to='course/resource/%Y/%m', verbose_name='下载地址')
    add_time = models.DateTimeField(default=datetime.now, verbose_name='添加时间')

    class Meta:
        verbose_name = '课程资源'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

