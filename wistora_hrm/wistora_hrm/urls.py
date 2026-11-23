
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        'api/admin/',
        include('admin_dashboard.urls')
    ),

    path(
        'api-auth/',
        include('rest_framework.urls')
    ),

    path('api/hr/', include('hr_dashboard.urls')),

    path(
        "api/technical-lead/",
        include("technical_lead_dashboard.urls")
    ),
    path(
    "api/auth/",
    include("authentication.urls")
    ),
    # Authentication APIs
    path(
        'api/auth/',include('admin_dashboard.auth_urls')
    ),
]
