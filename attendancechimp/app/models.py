"""
models.py — Data model for AttendanceChimp.

AttendanceChimp is an electronic class attendance tool.  Instructors create
courses and lectures; each lecture is assigned a random QR code.  Students
photograph the QR code and upload the image.  The system decodes the QR code,
matches it to a lecture, and records the attendance.

Entities
--------
- CourseProfile   : extends Django User → instructor-specific data
- StudentProfile  : extends Django User → student-specific data
- Course          : a course taught by one instructor
- Enrollment      : junction table linking students to courses
- Lecture         : a single class meeting (has a QR-code identifier)
- QRCodeUpload    : a student's uploaded QR-code photograph
"""
from datetime import datetime
from django.utils import timezone
from zoneinfo import ZoneInfo
from django.db import models
from django.contrib.auth.models import User

import logging
import string
import random

logger = logging.getLogger(__name__) # set up tracking, auditing, and debugging
                                                               # allows using logger.warning(), logger.error(), 
                                                               # logger.info(), etc. Better than print() for debuggin... 


# ---------------------------------------------------------------------------
# User profiles
# ---------------------------------------------------------------------------

class InstructorProfile(models.Model):
    """
    Represents an instructor for any given class. Only attribute will be instructor_id
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )

class StudentProfile(models.Model):
    """
    Represents a student for any given class. Only attribute will be student_id
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True
    )

# ---------------------------------------------------------------------------
# Course
# ---------------------------------------------------------------------------

class Course(models.Model):
    """
    Represents a course. Course attributes include course_id (primary key), name, 
    instructor_id (foreign key), schedule
    """
    course_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    instructor_id = models.ForeignKey(InstructorProfile, on_delete = models.CASCADE)
    schedule = models.CharField(max_length=200)
    course = models.CharField(max_length=100, unique=True, null=True, blank=True)

    mon = models.BooleanField(default=False)
    tue = models.BooleanField(default=False)
    wed = models.BooleanField(default=False)
    thu = models.BooleanField(default=False)
    fri = models.BooleanField(default=False)

    start_time = models.CharField(max_length=5, null=True, blank=True)
    end_time = models.CharField(max_length=5, null=True, blank=True)

    def meets_on_day(self, weekday):
        """
        Helper function that compiles the days in which the class meets in a list
        """
        days = [
            self.mon,
            self.tue,
            self.wed,
            self.thu,
            self.fri,
            False,
            False
        ]
        return days[weekday]

# ---------------------------------------------------------------------------
# Enrollment
# ---------------------------------------------------------------------------

class Enrollment(models.Model):
    """
    Represents junction table for students and courses.
    """
    student_id = models.ForeignKey(StudentProfile, on_delete = models.CASCADE)
    course_id = models.ForeignKey(Course, on_delete = models.CASCADE)
    
    class Meta:
        unique_together = ("student_id", "course_id")


# ---------------------------------------------------------------------------
# Lecture
# ---------------------------------------------------------------------------

class Lecture(models.Model):
    """
    Represents lectures from each course.
    """
    lecture_id = models.IntegerField(primary_key = True)
    course_id = models.ForeignKey(Course, on_delete = models.CASCADE)
    date = models.DateTimeField()
    qr_identifier = models.IntegerField(unique=True)

# ---------------------------------------------------------------------------
# QR Code Upload
# ---------------------------------------------------------------------------

class QRCodeUpload(models.Model):
    """
    Represents QR code sign ins among students
    """
    upload_id = models.AutoField(primary_key = True)
    student_id = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    lecture_id = models.ForeignKey(Lecture, on_delete=models.CASCADE, null=True, blank=True)
    image = models.FileField(upload_to="qr_uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

# ---------------------------------------------------------------------------
# Helper / API functions
# ---------------------------------------------------------------------------

def getUploadsForCourse(course):
    """
    Helper function that checks whether 1) checks if the given course refers to the current existing course
    2) Retrieves the QR Code upload 3) Checks if the upload was submitted during the class 
    4) Returns the uplaods only when all conditions are satisfied

    Parameters: 
        course: course number

    Return: the uplaods that satisfy the conditions for an upload for a course
    """

    try:
        course_obj = Course.objects.get(course=course)
    except Course.DoesNotExist:
        return []

    uploads = QRCodeUpload.objects.filter(lecture_id__course_id=course_obj)
    uploads_satisfied = []

    start = datetime.strptime(course_obj.start_time, "%H:%M").time()
    end = datetime.strptime(course_obj.end_time, "%H:%M").time()

    for upload in uploads:
       
        local_time = timezone.localtime(upload.uploaded_at, ZoneInfo("America/Chicago"))

        if not course_obj.meets_on_day(local_time.weekday()):
            continue

        if start <= local_time.time() <= end:
            uploads_satisfied.append(upload)

    return uploads_satisfied
