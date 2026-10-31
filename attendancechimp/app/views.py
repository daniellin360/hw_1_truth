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

from .models import InstructorProfile, StudentProfile

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



# ---------------------------------------------------------------------------
# HW6  — getUploads
# ---------------------------------------------------------------------------



