from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', CourseListView.as_view(), name='course_list'),
    url(r'^(?P<course_id>\d+)/$', CourseDetailView.as_view(), name='course_detail'),
    url(r'^video/(?P<course_id>\d+)', CourseVideoView.as_view(), name='course_video'),
    url(r'^comment/(?P<course_id>\d+)', CourseCommentView.as_view(), name='course_comment'),
    url(r'^play/(?P<video_id>\d+)', CoursePlayView.as_view(), name='course_play'),

    # 添加评论
    url(r'^add_comment/$', AddCommentView.as_view(), name='add_comment')

]