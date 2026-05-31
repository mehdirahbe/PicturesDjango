"""
URL configuration for PicturesDjango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings

"""
Clean URL configuration with i18n support.

All application URLs are placed inside i18n_patterns so that:
- They get a language prefix (/en/, /fr/)
- Django's LocaleMiddleware can properly detect and activate the language
  from the URL for the whole request.

This prevents the language from "resetting" when navigating through links.
"""

urlpatterns = []

# Everything that should support language switching goes here
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('PicturesApp.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
)

# Non-i18n URLs (debug toolbar, etc.)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
