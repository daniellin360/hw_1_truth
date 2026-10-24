
"""
LLM: OpenAI

Prompt:
Generate an alternative Django models.py for AttendanceChimp, an electronic attendance application. 
Include instructor and student profiles, courses, student enrollments, lectures with unique QR identifiers, 
and student QR code photo uploads. Design appropriate primary keys, foreign keys, and constraints. 
Include good docstrings.
"""

import uuid

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class InstructorProfile(models.Model):
    """
    Extends Django's built-in User model with an instructor role.

    Each instructor profile belongs to exactly one user.
    An instructor may teach multiple courses.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="instructor_profile"
    )

    department = models.CharField(
        max_length=100,
        blank=True
    )

    def __str__(self):
        return self.user.username


class StudentProfile(models.Model):
    """
    Extends Django's built-in User model with a student role.

    Each student profile belongs to one user.
    Students may enroll in multiple courses.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="student_profile"
    )

    student_number = models.CharField(
        max_length=30,
        unique=True
    )

    def __str__(self):
        return self.user.username


class Course(models.Model):
    """
    Represents a course taught by an instructor.

    Each course has one instructor, a name, and a meeting
    schedule. Students enroll through the Enrollment table.
    """

    id = models.BigAutoField(primary_key=True)

    name = models.CharField(max_length=200)

    instructor = models.ForeignKey(
        InstructorProfile,
        on_delete=models.CASCADE,
        related_name="courses"
    )

    schedule = models.CharField(max_length=200)

    students = models.ManyToManyField(
        StudentProfile,
        through="Enrollment",
        related_name="courses"
    )

    def __str__(self):
        return self.name


class Enrollment(models.Model):
    """
    Junction table connecting students to courses.

    A student may enroll in multiple courses, and a course
    may contain multiple students. The unique constraint
    prevents duplicate student-course enrollments.
    """

    id = models.BigAutoField(primary_key=True)

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    enrolled_at = models.DateTimeField(
        default=timezone.now
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"],
                name="unique_student_course_enrollment"
            )
        ]

    def __str__(self):
        return f"{self.student} - {self.course}"


class Lecture(models.Model):
    """
    Represents an individual class meeting.

    Each lecture belongs to one course and has a unique
    QR identifier used to identify the lecture when
    students submit QR code photographs.
    """

    id = models.BigAutoField(primary_key=True)

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lectures"
    )

    date = models.DateTimeField()

    qr_identifier = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    def __str__(self):
        return f"{self.course.name} - {self.date}"


class QRCodeUpload(models.Model):
    """
    Represents a QR code photograph uploaded by a student.

    Every upload belongs to a student. The lecture reference
    is optional because an uploaded QR code may not yet have
    been decoded or matched to a lecture.

    The image field stores the path to the uploaded photograph.
    """

    id = models.BigAutoField(primary_key=True)

    student = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="qr_uploads"
    )

    lecture = models.ForeignKey(
        Lecture,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="qr_uploads"
    )

    image = models.ImageField(
        upload_to="attendance/qr_uploads/"
    )

    uploaded_at = models.DateTimeField(
        default=timezone.now
    )

    is_verified = models.BooleanField(
        default=False
    )

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"Upload {self.pk} by {self.student}"
