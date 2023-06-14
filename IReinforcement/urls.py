"""
URL configuration for IReinforcement project.

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
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from IreinforcementLRP.views import upload_file,preview_story,get_scorm_data,update_scorm_data,process_300_chunks

urlpatterns = [
    path('upload', upload_file, name='upload-file'),
    path('<str:unique_id>/story.html', preview_story, name='preview-story'),
    path('scorm_data/<str:unique_id>', get_scorm_data, name='get_scorm_data'),
    path('scorm_data/<str:unique_id>', update_scorm_data, name='update_scorm_data'),
    path('https://sprinklezone.harbinger-systems.com',process_300_chunks,name='process_300_chunks'),
    
]

