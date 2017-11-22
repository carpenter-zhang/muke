from django.contrib import admin

from .models import UserAsk, CourseComment, UserFavorite, UserMessage, UserCourse


class UserAskAdmin(admin.ModelAdmin):
    list_display = ['name', 'course_name', 'add_time']
    list_filter = ['name', 'course_name', 'add_time']
    search_field = ['name', 'course_name', 'add_time']


class CourseCommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'add_time']
    list_filter = ['user', 'course', 'add_time']
    search_field = ['user', 'course', 'add_time']


class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'add_time', 'fav_type']
    list_filter = ['user', 'add_time', 'fav_type']
    search_field = ['user', 'add_time', 'fav_type']


class UserMessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'has_read', 'add_time']
    list_filter = ['user', 'has_read', 'add_time']
    search_field = ['user', 'has_read', 'add_time']


class UserCourseAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'add_time']
    list_filter = ['user', 'course', 'add_time']
    search_field = ['user', 'course', 'add_time']


admin.site.register(UserAsk, UserAskAdmin)
admin.site.register(CourseComment, CourseCommentAdmin)
admin.site.register(UserFavorite, UserFavoriteAdmin)
admin.site.register(UserMessage, UserMessageAdmin)
admin.site.register(UserCourse, UserCourseAdmin)