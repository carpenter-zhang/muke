from django.contrib import admin

from .models import Course, Lesson, Video, CourseResource


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0


class CourseResourceInline(admin.TabularInline):
    model = CourseResource
    extra = 0


class VideoInline(admin.StackedInline):
    model = Video


class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'degree', 'course_org', 'id']
    list_filter = ['name', 'degree', 'course_org']
    search_field = ['name', 'degree', 'course_org']
    inlines = [LessonInline, CourseResourceInline]


class LessonAdmin(admin.ModelAdmin):
    list_display = ['course', 'name']
    list_filter = ['course', 'name']
    search_field = ['course', 'name']
    inlines = [VideoInline]


class VideoAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'name']
    list_filter = ['lesson', 'name']
    search_field = ['lesson', 'name']


class CourseResourceAdmin(admin.ModelAdmin):
    list_display = ['course', 'name']
    list_filter = ['course', 'name']
    search_field = ['course', 'name']


admin.site.register(Course, CourseAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(CourseResource, CourseResourceAdmin)