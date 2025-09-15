from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core.views import home

urlpatterns = [
    path('admin/', admin.site.urls),

    # Login como página inicial
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),

    # Logout
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Home (segunda página tras login)
    path('home/', home, name='home'),
]
