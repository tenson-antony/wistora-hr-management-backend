
from django.contrib import admin

from .models import (
    Department,
    Designation,
    Employee,
    AcademicSession,
    SchoolClass,
    Subject,
    ClassSubjectAssignment,
    Student,
    StudentEnrollment,
    LeaveRequest,
    AttendanceRecord,
    SystemSetting,
    AuditLog,
    Notification,
)


# =====================================================
# 1. DEPARTMENT MANAGEMENT
# =====================================================

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'department_head',
        'created_at',
    )

    search_fields = (
        'name',
        'description',
    )

    ordering = ('name',)


# =====================================================
# 2. DESIGNATION MANAGEMENT
# =====================================================

@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
    )

    search_fields = ('name',)


# =====================================================
# 3. EMPLOYEE MANAGEMENT
# =====================================================

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'employee_id',
        'name',
        'email',
        'department',
        'designation',
        'status',
        'joining_date',
    )

    list_filter = (
        'status',
        'department',
        'designation',
    )

    search_fields = (
        'employee_id',
        'name',
        'email',
        'phone',
    )

    ordering = ('-created_at',)


# =====================================================
# 4. ACADEMIC SESSION MANAGEMENT
# =====================================================

@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'start_date',
        'end_date',
        'is_active',
    )

    list_filter = ('is_active',)

    search_fields = ('name',)


# =====================================================
# 5. SUBJECT MANAGEMENT
# =====================================================

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'code',
    )

    search_fields = (
        'name',
        'code',
    )


# =====================================================
# 6. CLASS SUBJECT INLINE
# =====================================================

class ClassSubjectAssignmentInline(admin.TabularInline):

    model = ClassSubjectAssignment

    extra = 1

    autocomplete_fields = (
        'subject',
        'teacher',
    )


# =====================================================
# 7. SCHOOL CLASS MANAGEMENT
# =====================================================

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'name',
        'section',
        'academic_session',
    )

    list_filter = ('academic_session',)

    search_fields = ('name', 'section')

    inlines = [
        ClassSubjectAssignmentInline,
    ]


# =====================================================
# 8. CLASS SUBJECT ASSIGNMENT MANAGEMENT
# =====================================================

@admin.register(ClassSubjectAssignment)
class ClassSubjectAssignmentAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'school_class',
        'subject',
        'teacher',
        'assigned_at',
    )

    list_filter = (
        'school_class',
        'subject',
    )

    autocomplete_fields = (
        'school_class',
        'subject',
        'teacher',
    )


# =====================================================
# 9. STUDENT MANAGEMENT
# =====================================================

class StudentEnrollmentInline(admin.TabularInline):

    model = StudentEnrollment

    extra = 1

    autocomplete_fields = ('school_class',)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'student_id',
        'name',
        'email',
        'phone',
        'status',
        'admission_date',
    )

    list_filter = ('status',)

    search_fields = (
        'student_id',
        'name',
        'email',
    )

    inlines = [
        StudentEnrollmentInline,
    ]


# =====================================================
# 10. STUDENT ENROLLMENT MANAGEMENT
# =====================================================

@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'student',
        'school_class',
        'enrollment_date',
        'status',
    )

    list_filter = (
        'status',
        'school_class',
    )

    search_fields = (
        'student__name',
        'student__student_id',
    )

    autocomplete_fields = (
        'student',
        'school_class',
    )


# =====================================================
# 11. LEAVE MANAGEMENT
# =====================================================

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'employee',
        'start_date',
        'end_date',
        'status',
        'reviewed_by',
        'created_at',
    )

    list_filter = (
        'status',
        'start_date',
    )

    search_fields = (
        'employee__name',
        'employee__employee_id',
        'reason',
    )

    readonly_fields = (
        'created_at',
    )


# =====================================================
# 12. ATTENDANCE MANAGEMENT
# =====================================================

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'employee',
        'date',
        'status',
        'check_in',
        'check_out',
    )

    list_filter = (
        'status',
        'date',
    )

    search_fields = (
        'employee__name',
        'employee__employee_id',
    )

    date_hierarchy = 'date'


# =====================================================
# 13. SYSTEM SETTINGS
# =====================================================

@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'organization_name',
        'organization_email',
        'organization_phone',
        'updated_at',
    )

    search_fields = (
        'organization_name',
        'organization_email',
    )

    readonly_fields = (
        'updated_at',
    )


# =====================================================
# 14. AUDIT LOG MANAGEMENT
# =====================================================

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'action',
        'module',
        'ip_address',
        'created_at',
    )

    list_filter = (
        'module',
        'action',
        'created_at',
    )

    search_fields = (
        'user__username',
        'action',
        'module',
        'description',
    )

    readonly_fields = (
        'user',
        'action',
        'module',
        'description',
        'ip_address',
        'created_at',
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff


# =====================================================
# 15. NOTIFICATION MANAGEMENT
# =====================================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'recipient',
        'title',
        'is_read',
        'created_at',
    )

    list_filter = (
        'is_read',
        'created_at',
    )

    search_fields = (
        'recipient__username',
        'title',
        'message',
    )

    readonly_fields = (
        'created_at',
    )
