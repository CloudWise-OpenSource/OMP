"""omp_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, include

# coreAPI documentation
from rest_framework.documentation import include_docs_urls
from rest_framework.permissions import AllowAny

from users.urls import router as users_router
from users.views import JwtAPIView

# from hosts.urls import router as hosts_router

urlpatterns_inside = [
    path("login/", JwtAPIView.as_view()),
    path("users/", include(users_router.urls)),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(urlpatterns_inside)),
    path("docs/", include_docs_urls(
        title="API 接口文档",
        permission_classes=(AllowAny,),
    ), name="docs"),
]
