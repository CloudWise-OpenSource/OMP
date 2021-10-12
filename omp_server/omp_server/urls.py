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
from django.urls import path, include, re_path

# coreAPI documentation
from rest_framework.documentation import include_docs_urls
from rest_framework.permissions import AllowAny
from rest_framework.authentication import (
    SessionAuthentication, BasicAuthentication
)

from users.urls import router as users_router
from users.views import JwtAPIView

from hosts.urls import router as hosts_router
from app_store.urls import router as app_store_router
from promemonitor.urls import router as promemonitor_router
from promemonitor.grafana_views import grafana_proxy_view

urlpatterns_inside = [
    path("login/", JwtAPIView.as_view(), name="login"),
    path("users/", include(users_router.urls), name="users"),
    path("hosts/", include(hosts_router.urls), name="hosts"),
    path("appStore/", include(app_store_router.urls), name="appStore"),
    path("promemonitor/",
         include(promemonitor_router.urls), name="promemonitor"),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(urlpatterns_inside)),
    path("docs/", include_docs_urls(
        title="API 接口文档",
        authentication_classes=(
            SessionAuthentication, BasicAuthentication),
        permission_classes=(AllowAny,),
    ), name="docs"),
    re_path(r'^proxy/v1/grafana/(?P<path>.*)', grafana_proxy_view),
]
