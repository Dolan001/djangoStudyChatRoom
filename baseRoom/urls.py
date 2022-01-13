from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('chatRoom.urls')),
    path('api/', include('chatRoom.api.urls')),
]
