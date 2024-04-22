from django.contrib import admin
from django.urls import path, include

from django.contrib.staticfiles.urls import staticfiles_urlpatterns  # Correct import for staticfiles_urlpatterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('investment_management.urls')),  # Include app's URLs here
 
]
urlpatterns += staticfiles_urlpatterns()