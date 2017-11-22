from django.conf.urls import url, include

from .views import *

urlpatterns = [
    url(r'^$', OrgListView.as_view(), name='org_list'),
    url(r'^add_ask/$', AddUserAskView.as_view(), name='add_ask'),
    url(r'^home/(?P<org_id>\d+)/$', OrgHomeView.as_view(), name='org_home'),
    url(r'^course/(?P<org_id>\d+)/$', OrgCourseView.as_view(), name='org_course'),
    url(r'^desc/(?P<org_id>\d+)/$', OrgDescView.as_view(), name='org_desc'),
    #  机构详情页面的教师列表
    url(r'^teacher/(?P<org_id>\d+)/$', OrgTeacherView.as_view(), name='org_teacher'),

    url(r'^add_fav/$', AddFavView.as_view(), name='add_fav'),

    url(r'^teacher/$', TeacherListView.as_view(), name='teacher_list'),
    url(r"^teacher_detail/(?P<teacher_id>\d+)/$", TeacherDetailView.as_view(), name='teacher_detail')

]
