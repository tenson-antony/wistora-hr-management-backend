
from django.db import models
from django.conf import settings
from django.db.models import Q, F
from django.utils import timezone


# =====================================================
# 1. DEPARTMENT MANAGEMENT
# =====================================================

class Department(models.Model):

    name = models.CharField(max_length=150, unique=True)

    description = models.TextField(blank=True)

    department_head = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='headed_departments'
    )
    

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =====================================================
# 2. DESIGNATION MANAGEMENT
# =====================================================

class Designation(models.Model):

    name = models.CharField(max_length=100, unique=True)

    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


# =====================================================
# 3. EMPLOYEE MANAGEMENT
# =====================================================

class Employee(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('resigned', 'Resigned'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_profile'
    )

    employee_id = models.CharField(
        max_length=30,
        unique=True
    )

    name = models.CharField(max_length=150)

    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=15, blank=True)

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )

    designation = models.ForeignKey(
        Designation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )

    joining_date = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee_id} - {self.name}"


# =====================================================
# 4. ACADEMIC SESSION MANAGEMENT
# =====================================================

class AcademicSession(models.Model):

    name = models.CharField(max_length=100, unique=True)

    start_date = models.DateField()

    end_date = models.DateField()

    is_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# =====================================================
# 5. SUBJECT MANAGEMENT
# =====================================================

class Subject(models.Model):

    name = models.CharField(max_length=100)

    code = models.CharField(
        max_length=30,
        unique=True
    )

    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


# =====================================================
# 6. CLASS MANAGEMENT
# =====================================================

class SchoolClass(models.Model):

    name = models.CharField(max_length=100)

    section = models.CharField(
        max_length=20,
        blank=True
    )

    academic_session = models.ForeignKey(
        AcademicSession,
        on_delete=models.PROTECT,
        related_name='classes'
    )

    subjects = models.ManyToManyField(
        Subject,
        through='ClassSubjectAssignment',
        related_name='school_classes',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'section', 'academic_session'],
                name='unique_class_section_per_session'
            )
        ]

    def __str__(self):
        return f"{self.name} - {self.section}"


# =====================================================
# 7. CLASS, SUBJECT AND TEACHER ASSIGNMENT
# =====================================================

class ClassSubjectAssignment(models.Model):

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name='subject_assignments'
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name='class_assignments'
    )

    teacher = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teaching_assignments'
    )

    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['school_class', 'subject'],
                name='unique_subject_per_school_class'
            )
        ]

    def __str__(self):
        return f"{self.school_class} - {self.subject}"


# =====================================================
# 8. STUDENT MANAGEMENT
# =====================================================

class Student(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graduated'),
    ]

    student_id = models.CharField(
        max_length=30,
        unique=True
    )

    name = models.CharField(max_length=150)

    email = models.EmailField(blank=True)

    phone = models.CharField(max_length=15, blank=True)

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    admission_date = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student_id} - {self.name}"


# =====================================================
# 9. STUDENT ENROLLMENT MANAGEMENT
# =====================================================

class StudentEnrollment(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('transferred', 'Transferred'),
        ('withdrawn', 'Withdrawn'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.PROTECT,
        related_name='enrollments'
    )

    enrollment_date = models.DateField(
        default=timezone.localdate
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'school_class'],
                name='unique_student_class_enrollment'
            )
        ]

    def __str__(self):
        return f"{self.student.name} - {self.school_class}"


# =====================================================
# 10. LEAVE MANAGEMENT
# =====================================================

class LeaveRequest(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )

    start_date = models.DateField()

    end_date = models.DateField()

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    reviewed_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_leave_requests'
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__gte=F('start_date')),
                name='leave_end_date_after_start_date'
            )
        ]

    def __str__(self):
        return f"{self.employee.name} - {self.status}"


# =====================================================
# 11. ATTENDANCE MANAGEMENT
# =====================================================

class AttendanceRecord(models.Model):

    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('half_day', 'Half Day'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )

    date = models.DateField(
        default=timezone.localdate
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    check_in = models.TimeField(
        null=True,
        blank=True
    )

    check_out = models.TimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'date'],
                name='unique_employee_attendance_per_day'
            ),
            models.CheckConstraint(
                condition=(
                    Q(check_in__isnull=True) |
                    Q(check_out__isnull=True) |
                    Q(check_out__gte=F('check_in'))
                ),
                name='attendance_checkout_after_checkin'
            )
        ]

    def __str__(self):
        return f"{self.employee.name} - {self.date}"


# =====================================================
# 12. SYSTEM SETTINGS
# =====================================================

class SystemSetting(models.Model):

    organization_name = models.CharField(max_length=200)

    organization_email = models.EmailField(blank=True)

    organization_phone = models.CharField(
        max_length=20,
        blank=True
    )

    address = models.TextField(blank=True)

    logo = models.ImageField(
        upload_to='organization/',
        null=True,
        blank=True
    )

    configuration = models.JSONField(
        default=dict,
        blank=True
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.organization_name


# =====================================================
# 13. AUDIT LOG MANAGEMENT
# =====================================================

class AuditLog(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )

    action = models.CharField(max_length=100)

    module = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.module} - {self.action}"


# =====================================================
# 14. NOTIFICATION MANAGEMENT
# =====================================================

class Notification(models.Model):

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    title = models.CharField(max_length=200)

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
