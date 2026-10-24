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

# ---------------------------------------------------------------------------
# Enrollment
# ---------------------------------------------------------------------------

class Enrollment(models.Model):
    """
    Represents junction table for students and courses.
    """
    student_id = models.ForeignKey(StudentProfile, on_delete = models.CASCADE)
    course_id = models.ForeignKey(Course, on_delete = models.CASCADE)
    pk = models.CompositePrimaryKey("student_id", "course_id")


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
    image = models.FileField(upload_to="qr_uploads/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

# ---------------------------------------------------------------------------
# Helper / API functions
# ---------------------------------------------------------------------------



