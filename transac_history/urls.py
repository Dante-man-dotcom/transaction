"""
URL configuration for transac_history project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from transac_app.views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', loginpage, name='loginpage'),
    path('login/', login, name='login'),
    path('register/', register, name='register'),
    path('home/', home, name='home'),
    path('transac_create/', transac_create, name='transac_create'),
    path('acknowledgement/<int:ack_id>/<str:action>/', ack_action, name='ack_action'),
    path('transac/', transac, name='transac'),
    path('tansac_history/', transac_history, name='transac_history'),
    path('tansac_filter/', transac_filter, name='transac_filter'),
    path('logout/', my_logout, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
