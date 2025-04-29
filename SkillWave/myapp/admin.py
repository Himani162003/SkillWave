from django.contrib import admin

admin.site.site_header = "SkillWave Administration"
admin.site.site_title = "SkillWave Admin Portal"
admin.site.index_title = "Welcome to SkillWave Admin Panel"
# index_templates = "admin/custom_index.html"


from django.contrib import admin
# from .models import Admin
from . import models

class AdminAdmin(admin.ModelAdmin):
    list_display = ('admin_id', 'name', 'email')  # Display admin_id, name, and email in the admin panel

admin.site.register(models.Admin, AdminAdmin)
admin.site.register(models.Member)


# # Register your models here.
# admin.site.register(models.Student)

# class Stusent(admin.ModelAdmin):
#     list_display = (    
#     "student_id",
#     "enrollment",
#     "name",
#     "address",
#     "phone_no",
#     "course",
#     "email",
#     "DOB",
#     )

from .models import Student
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'address', 'phone_no', 'email', 'DOB')  # Display all fields in table format
    search_fields = ('name', 'email')  # Enables search functionality
    list_filter = ('DOB',)  # Adds filter sidebar
    ordering = ('student_id',)  # Orders by student ID
    list_per_page = 20  # Pagination for better readability

admin.site.register(Student, StudentAdmin)




# # Register your models here.
# admin.site.register(models.Course)

# class Course(admin.ModelAdmin):
#     list_display = (    
#     "course_id",
#     "course_name",
#     "duration",
#     "fees",
#     )

from .models import Course, Student

class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'course_name', 'duration', 'fees')  # Fields displayed in table format
    list_filter = ('duration',)  # Filter option in admin panel
    search_fields = ('course_name',)  # Search by course name
    ordering = ('course_id',)  # Default ordering by course_id

admin.site.register(Course, CourseAdmin)



# # Register your models here.
# admin.site.register(models.Enrollment)

# class Enrollment(admin.ModelAdmin):
#     list_display = (     
#     "student_id",
#     "course_id",
#     "fees",
#     "admission_date",
#     "start_date",
#     "end_date",
#     "enroll_id",
#     )
from .models import Enrollment

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('enroll_id', 'course_name', 'admission_date', 'start_date')
    list_filter = ('admission_date', 'start_date', 'course_name')
    search_fields = ('student_id__id', 'course_name', 'enroll_id')
    ordering = ('-admission_date',)

    # def get_student_id(self, obj):
    #     return obj.student_id.id  # Displaying only student ID
    # get_student_id.admin_order_field = 'student_id'  
    # get_student_id.short_description = 'Student ID'

    # def get_course_name(self, obj):
    #     return obj.course_name.name  # Displaying only course ID
    # get_course_name.admin_order_field = 'course_name'  
    # get_course_name.short_description = 'Course name'

admin.site.register(Enrollment, EnrollmentAdmin)



# # Register your models here.
# admin.site.register(models.Idcard)

# class Idcard(admin.ModelAdmin):
#     list_display = (   
#     "card_id", 
#     "course_id", 
#     "student_id",
#     "issue_date",
#     )
from .models import Idcard

# class IdcardAdmin(admin.ModelAdmin):
#     list_display = ('card_id', 'course_id', 'student_id__name', 'issue_date')  # Display columns in table format
#     list_filter = ('course_id', 'issue_date')  # Add filtering options
#     search_fields = ('card_id', 'student_id__id')  # Enable search functionality
#     ordering = ('-issue_date',)  # Order by issue_date in descending order

# admin.site.register(Idcard, IdcardAdmin)
admin.site.register(Idcard)

# def get_photo(self,obj):
#     return obj.photo
# get_photo.short_description = 'Photo'



# class AdminAdmin(admin.ModelAdmin):
#     list_display = ('admin_id', 'name', 'email')  # Display admin_id, name, and email in the admin panel

# admin.site.register(models.Admin, AdminAdmin)



# from .models import Fees

# class FeesAdmin(admin.ModelAdmin):
#     list_display = ('student_name','receipt_no','enrollment_id','course_name','total_amount','paid_amount','total_paid_amount','payment_mode','received_date')
#     list_filter = ('payment_mode', 'received_date', 'course_name')
#     search_fields = ('receipt_no', 'enrollment_id')
#     ordering = ('-received_date',)
    
# #     # def get_student_name(self, obj):
# #     #     return obj.enrollment.student_id.name
# #     # get_student_name.short_description = 'Student Name'

# admin.site.register(Fees, FeesAdmin)

# Fees Model
class FeesAdmin(admin.ModelAdmin):
    list_display = ('receipt_no', 'student', 'get_enrollment_id', 'get_course_name', 'total_amount', 'total_paid_amount', 'get_remaining_amount', 'paid_amount', 'get_payment_mode', 'received_date')
    list_filter = ('payment_mode', 'received_date', 'course_name')
    search_fields = ('receipt_no', 'student', 'enrollment_id__enroll_id')
    ordering = ('-received_date',)
    date_hierarchy = 'received_date'
    list_per_page = 20
    icon_name = 'payments'

    def get_enrollment_id(self, obj):
        return obj.enrollment_id.student_id.name
    get_enrollment_id.short_description = 'Student Name'
    get_enrollment_id.admin_order_field = 'enrollment_id__student_id__name'

    def get_course_name(self, obj):
        return obj.course_name.course_name
    get_course_name.short_description = 'Course Name'
    get_course_name.admin_order_field = 'course_name__course_name'

    def get_remaining_amount(self, obj):
        remaining = obj.total_amount - obj.total_paid_amount
        return f"₹{remaining:,.2f}"
    get_remaining_amount.short_description = 'Remaining Amount'
    get_remaining_amount.admin_order_field = 'total_amount'

    def get_payment_mode(self, obj):
        return dict(models.Fees.PAYMENT_MODE_CHOICES)[obj.payment_mode]
    get_payment_mode.short_description = 'Payment Mode'
    get_payment_mode.admin_order_field = 'payment_mode'

    fieldsets = (
        ('Basic Information', {
            'fields': ('student', 'enrollment_id', 'course_name', 'received_date')
        }),
        ('Payment Details', {
            'fields': ('total_amount', 'paid_amount', 'total_paid_amount', 'payment_mode')
        }),
        ('Payment Mode Details', {
            'fields': ('upi_id', 'bank_transfer_id', 'credit_card_number', 'debit_card_number', 'net_banking_id'),
            'classes': ('collapse',),
            'description': 'Additional details based on payment mode'
        }),
    )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:  # This is an edit form
            payment_mode = obj.payment_mode
            payment_fields = []
            if payment_mode == '2':  # UPI
                payment_fields = ['upi_id']
            elif payment_mode == '3':  # Bank Transfer
                payment_fields = ['bank_transfer_id']
            elif payment_mode == '5':  # Credit Card
                payment_fields = ['credit_card_number']
            elif payment_mode == '6':  # Debit Card
                payment_fields = ['debit_card_number']
            elif payment_mode == '7':  # Net Banking
                payment_fields = ['net_banking_id']
            
            if payment_fields:
                fieldsets = (
                    ('Basic Information', {
                        'fields': ('student', 'enrollment_id', 'course_name', 'received_date')
                    }),
                    ('Payment Details', {
                        'fields': ('total_amount', 'paid_amount', 'total_paid_amount', 'payment_mode')
                    }),
                    ('Payment Mode Details', {
                        'fields': payment_fields,
                        'classes': ('collapse',),
                        'description': 'Additional details based on payment mode'
                    }),
                )
        return fieldsets

admin.site.register(models.Fees, FeesAdmin)

