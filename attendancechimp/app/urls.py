from django.urls import path
from . import views

urlpatterns = [
    path('time', views.time_view, name='time'),
    path('sum', views.sum_view, name='sum'),
    path('', views.index, name='home'),
    path('index.html', views.index, name='index_html'),
    path('new', views.new, name='new'),
    path('createUser', views.createUser, name='createUser'),
    path('new_course', views.new_course, name='newCourse'),
    path('new_lecture', views.new_lecture, name='newLecture'),
    path('new_qr_upload', views.new_qr_upload, name='newQRUpload'),
    path('createCourse', views.create_course, name='createCourse'),
    path('createLecture', views.create_lecture, name='createLecture'),
    path('createQRCodeUpload', views.create_qr_code_upload, name='createQRCodeUpload'),
    path('dumpUploads', views.dump_uploads, name='dumpUploads'),
    path('getUploads', views.getUploads, name='getUploads')
]