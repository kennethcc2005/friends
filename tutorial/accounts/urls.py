from django.conf.urls import url, include
from accounts import views
from rest_framework.routers import DefaultRouter

from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken import views as rest_framework_views

urlpatterns = [
    # url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # Session Login
    # url(r'^login/$', local_views.get_auth_token, name='login'),
    # url(r'^logout/$', local_views.logout_user, name='logout'),
    # url(r'^auth/$', local_views.login_form, name='login_form'),
    # url(r'^api-token-auth/$', rest_framework_views.obtain_auth_token, name='get_auth_token'),
    # url(r'^register', views.create_auth, name='register_user'),
    url(r'^register', views.CreateUserView, name='register_user'),
    # url(r'^api/', include(router.urls)),
]