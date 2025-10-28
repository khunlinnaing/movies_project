from django.urls import path
from project import views
app_name = 'website'
urlpatterns = [
    path('', views.index, name='index-view'),
    path('login/get', views.login_view, name="login-view-get"),
    path('login/post', views.login_view_post, name="login-view-post"),
    path('logout', views.logout_view, name="logout-view"),
    path('signup', views.signup_view, name="signup-view"),
]