"""
views.py — HTTP request handlers for AttendanceChimp.

Each view corresponds to one URL endpoint.  Views receive an HTTP request,
interact with the database via models.py, and return an HTTP response.
"""

from django.shortcuts import render, redirect
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseBadRequest, JsonResponse)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from datetime import datetime
import zoneinfo
import json
import io
import random

from .models import InstructorProfile, StudentProfile, Course, Lecture, QRCodeUpload

CDT = zoneinfo.ZoneInfo("America/Chicago")


# ---------------------------------------------------------------------------
# HW2  — index, time, sum
# ---------------------------------------------------------------------------

def index(request):
    """Render the home page (index.html)."""

    now = datetime.now(CDT)
    hour_min = now.strftime("%H:%M")

    context = {"current_time": hour_min, "user": request.user}

    return render(request, 'app/index.html', context)

def time_view(request):
    """Converts to Central Time formatted as HH:MM"""

    now = datetime.now(CDT)
    hour_min = now.strftime("%H:%M")
    return HttpResponse(hour_min, content_type="text/plain")

def sum_view(request):
    """Adds URL path for sum"""

    n1 = float(request.GET.get("n1"))
    n2 = float(request.GET.get("n2"))
    sum = n1 + n2
    return HttpResponse(f"<p>{sum}</p>")


# ---------------------------------------------------------------------------
# HW4  — user creation
# ---------------------------------------------------------------------------

def new(request):
    if request.method != "GET":
        return HttpResponseBadRequest("Accepts only GET requests")

    return render(request, 'app/new.html')

@csrf_exempt
def createUser(request):
    """
    Creates a new user withe the data provided
    """

    if request.method != "POST":
        return HttpResponseBadRequest("Only accepts POST")
    
    user_name = request.POST.get("user_name")
    email = request.POST.get("email")
    password = request.POST.get("password")
    is_student = request.POST.get("is_student")

    if User.objects.filter(email=email).exists():
        return HttpResponseBadRequest("Email already exists")

    user = User.objects.create_user(username=user_name, email=email, password=password)
    
    if is_student == "1":
        StudentProfile.objects.create(user=user)
    else:
        InstructorProfile.objects.create(user=user)

    login(request, user)

    return HttpResponse("User created", status = 200)

# ---------------------------------------------------------------------------
# HW5  — courses, lectures, QR uploads, dump
# ---------------------------------------------------------------------------

def new_course(request):
    """
    Renders HTML form of creating new course
    """
    
    return render(request, 'app/new_course.html')

def new_lecture(request):
    """
    Renders HTML form of creating new lecture
    """

    return render(request, 'app/new_lecture.html')

def new_qr_upload(request):
    """
    Renders HTML form of creating new QR Upload
    """

    return render(request, 'app/new_qr_upload.html')

@csrf_exempt
def createCourse(request):
    """
    Allows instructors to create new courses
    """

    if request.method != "POST":
        return HttpResponseBadRequest("Only accepts POST")
    
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    
    if not InstructorProfile.objects.filter(user=request.user).exists():
        return HttpResponse("Not instructor", status=401)

    course_name = request.POST.get("course-name")
    start_time = request.POST.get("start-time")
    end_time = request.POST.get("end-time")

    selected_days = [day for day in ["mon", "tue", "wed", "thu", "fri"] if f"day-{day}" in request.POST]

    if not course_name or not start_time or not end_time or not selected_days:
        return HttpResponseBadRequest("Missing required information")

    schedule = f"{','.join(selected_days)} {start_time}-{end_time}"
    course_id = max(Course.objects.values_list("course_id", flat=True), default=0) + 1
    instructor = InstructorProfile.objects.get(user=request.user)

    Course.objects.create(course_id=course_id, name=course_name, instructor_id=instructor, schedule=schedule)

    return HttpResponse("Course created", status = 200)

@csrf_exempt
def createLecture(request):
    """
    Creates new lecture for a course
    """

    if request.method != "POST":
        return HttpResponseBadRequest("Only accepts POST")
    
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    
    if not InstructorProfile.objects.filter(user=request.user).exists():
        return HttpResponse("Not instructor", status=401)

    course_name = request.POST.get("choice")

    course = Course.objects.filter(name=course_name).first()
    if course is None:
        return HttpResponseBadRequest("Course not found")

    lecture_id = max(Course.objects.values_list("lecture_id", flat=True), default=0) + 1
    date = datetime.now()
    qr_identifier = random.randint(100000, 999999)

    while Lecture.objects.filter(qr_identifier=qr_identifier).exists():
        qr_identifier = random.randint(100000, 999999)
    
    Lecture.objects.create(lecture_id=lecture_id, course_id=course, date=date, qr_identifier=qr_identifier)

    return HttpResponse("Lecture created", status=200)

@csrf_exempt
def createQRCodeUpload(request):
    """
    Creates a place for Students to upload QRs
    """

    if request.method != "POST":
        return HttpResponseBadRequest("Only accepts POST")
    
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    
    if not StudentProfile.objects.filter(user=request.user).exists():
        return HttpResponse("Not student", status=401)

    image = request.FILES.get("imageUpload")
    student = StudentProfile.objects.get(user=request.user)

    QRCodeUpload.objects.create(student_id=student, image=image)
    return HttpResponse("QR code upload", status=200)

def dumpUploads(request):
    """
    Returns JSON list of dictionaries of students QR uploads
    """

    if request.method != "GET":
        return HttpResponseBadRequest("Only accepts GET")
    
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    
    if not InstructorProfile.objects.filter(user=request.user).exists():
        return HttpResponse("Not instructor", status=401)

    uploads = QRCodeUpload.objects.all()

    codesInfo = []

    for upload in uploads:
        codesInfo.append({"username": upload.student_id.user.username, "upload_time": upload.uploaded_at.strftime("%Y-%m-%d %H:%M:%S")})

    return JsonResponse(codesInfo, safe=False)

# ---------------------------------------------------------------------------
# HW6  — getUploads
# ---------------------------------------------------------------------------



