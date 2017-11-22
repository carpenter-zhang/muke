from django.conf.urls import url
from .views import UserInfoView, UserCourseView, UserMessageView, UserFavCourseView, UserFavTeacherView, \
    UserFavOrgView, UploadImageView, UpdatePwdView, UpdateEmailView, SendEmailCodeView
#
urlpatterns = [
    url('^info/$', UserInfoView.as_view(), name='user_info'),
    url('^course/$', UserCourseView.as_view(), name='user_course'),
    url('^message/$', UserMessageView.as_view(), name='user_message'),

    url('^fav_course/$', UserFavCourseView.as_view(), name='user_fav_course'),
    url('^fav_teacher/$', UserFavTeacherView.as_view(), name='user_fav_teacher'),
    url('^fav_org/$', UserFavOrgView.as_view(), name='user_fav_org'),

    # 头像修改
    url('^image/upload/$', UploadImageView.as_view(), name='image_upload'),
    # 修改密码
    url('^update/pwd/$', UpdatePwdView.as_view(), name='update_pwd'),
    # 修改邮箱
    url('^update_email/$', UpdateEmailView.as_view(), name='update_email'),

    url('^sendemail_code/$', SendEmailCodeView.as_view(), name='sendemail_code'),

]