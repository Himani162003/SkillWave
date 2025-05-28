from django.shortcuts import render, redirect
from . import models    
from datetime import datetime
from dateutil.relativedelta import relativedelta
import base64
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import qrcode
import os
from decimal import Decimal 
from num2words import num2words 
from django.contrib import messages
from django.conf import settings
from PIL import Image
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import render_to_string
from django.db.models import Count

import pdfkit

def add_months(start_date_str, months_to_add):
                """
                Calculates a new date by adding a specified number of months to a start date.

                Args:
                    start_date_str (str): The starting date in 'YYYY-MM-DD' format.
                    months_to_add (int): The number of months to add (can be positive or negative).

                Returns:
                    str: The calculated date in 'YYYY-MM-DD' format, or None if an error occurs.
                """
                
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                months_to_add = int(months_to_add)  # 🔥 Force it to integer
                new_date = start_date + relativedelta(months=months_to_add)
                return new_date.strftime('%Y-%m-%d')
                

def Admin_Register(request): 
    print("Register view accessed")  # Debugging line to check if the view is called

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        name = request.POST.get('name')
        retype_password = request.POST.get('retype_password')
        if password == retype_password:
            if models.Admin.objects.filter(email=email).count() == 1:
                return render(request, 'admin_register.html', {'error': "Admin already exists"})  # Return an error message if the user already exists
            
            models.Admin.objects.create(
                email=email, 
                password=password, 
                name=name
            )
            return render(request, 'admin_login.html')
        else:
            return render(request,'admin_register.html', {'error': "Password don't match with Re-type Password"})
    return render(request,'admin_register.html')

# Create your views here.
def Member_Register(request,admin_id): 
    print("Register view accessed")  # Debugging line to check if the view is called
    admin = models.Admin.objects.get(admin_id=admin_id)
    context = {
        'id' : admin.admin_id,  # Ensure this is correctly set without trailing spaces
    }
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        name = request.POST.get('name')
        mobile_number = request.POST.get('mobile_number')
        date_of_joining = request.POST.get('date_of_joining')
        retype_password = request.POST.get('retype_password')
        admin = models.Admin.objects.get(admin_id=admin_id)  # Retrieve the Admin instance

        if password == retype_password:
            if models.Member.objects.filter(member_email=email).count() == 1:
                return render(request, 'member_register.html', {'error': "User already exists"})  # Return an error message if the user already exists
            
            models.Member .objects.create(
                member_email=email, 
                member_password=password, 
                member_name=name,
                member_phone=mobile_number,
                date_of_joining=date_of_joining,
                admin=admin
            )
            return redirect('admin_dashboard', admin_id=admin_id)  # Redirect to the admin dashboard after successful registration
        else:
            return render(request,'member_register.html', {'error': "Password don't match with Re-type Password"})
    return render(request,'member_register.html',context)




def Admin_Login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        c = models.Admin.objects.get(email=email)

        print("admin+++++++",c)
        if c:
            id = c.admin_id  # Accessing admin_id from the single instance
            if c.password == password:
                admin_id = c.admin_id  # Retrieve the admin_id from the Admin instance
                # Fetching the admin instance
                total_students = models.Student.objects.filter(admin_id=admin_id).count()
                total_courses = models.Course.objects.filter(admin_id=admin_id).count()
                total_enrollments = models.Enrollment.objects.filter(admin_id=admin_id).count()
                total_idcards = models.Idcard.objects.filter(enrollment__admin_id=admin_id).count()
                total_fees = models.Fees.objects.filter(admin_id=admin_id).count()
                total_fees_count = models.Fees.objects.filter(admin_id=admin_id).values(
                    'student__student_id'  
                ).annotate(
                    enroll_count=Count('receipt_no')
                ).count()
                total_certificates = models.Enrollment.objects.filter(admin_id=admin_id,payment_status="PAID").count()

                # Total counts
                total_students = models.Student.objects.filter(admin_id=admin_id).count()

                # Gender ratio for the chart
                registered_students = models.Student.objects.filter(admin_id=admin_id).count()
                enrolled_students = models.Enrollment.objects.filter(admin_id=admin_id)
                enrolled_students_count = enrolled_students.count()
                c = enrolled_students.filter(admin_id=admin_id,course_name_id = 1).count()
                print("enrolled students",c)
                top_courses = models.Enrollment.objects.filter(admin_id=admin_id).values(
                    'course_name__course_name'   # Assuming ForeignKey is 'course_name' in Enrollment model
                ).annotate(
                    enroll_count=Count('enroll_id')
                ).order_by('-enroll_count')[:3]  # Top 3 courses



                male_students = models.Student.objects.filter(admin_id=admin_id, gender='Male').count()
                female_students = models.Student.objects.filter(admin_id=admin_id, gender='Female').count()

                # Top students based on marks
                # top_students = models.Student.objects.filter(admin_id=admin_id).order_by('-marks')[:5]  # Top 5 students
                top_students = models.Enrollment.objects.filter(admin_id=admin_id)  # Top 5 students
                context = {
                    'id': id,
                    'user': c,
                    'total_students': total_students,
                    'total_courses': total_courses,
                    'total_enrollments': total_enrollments,
                    'total_idcards': total_idcards,
                    'total_fees': total_fees_count,
                    'total_certificates': total_certificates,
                    'registered_students': registered_students,
                    'enrolled_students': enrolled_students_count,
                    'male_students': male_students,
                    'female_students': female_students,
                    'top_students': top_students,
                    'top_courses': top_courses,
                    # 'popular_courses': popular_courses,
                    # 'no_of_enroll_student_in_each_course': no_of_enroll_student_in_each_course,
                    
                }
                return render(request,"admin_dashboard.html",context) 
            else:
                return render(request, 'admin_login.html', {'error': 'Wrong password!!'})
        else:
            return render(request, 'admin_login.html', {'error': 'You are not registered!!'})
    return render(request, 'admin_login.html')


def Member_Login(request):
    if request.method == 'POST':
        member_email = request.POST.get('email')
        member_password = request.POST.get('password')
        confirm = models.Member.objects.filter(member_email=member_email).exists()

        print("admin+++++++",confirm)
        if confirm:
            c = models.Member.objects.get(member_email=member_email)  # Retrieve the Member instance

            id = c.member_id  # Accessing member_id from the single instance
            if c.member_password == member_password:
                context = {
                    'id': id,
                    'user': c,
                    'admin': c.admin,  # Accessing the related Admin instance
                    'member': c,
                }
                return render(request,'index.html', context)  # Redirect to index with admin_id
            else:
                return render(request, 'member_login.html', {'error': 'Wrong password!!'})
        else:
            return render(request, 'member_login.html', {'error': 'You are not registered in any admin!!'})
    return render(request, 'member_login.html')


# def Dashboard(request):
#     # c = models.Admin.objects.get(admin_id=admin_id)
#     # id = c.admin_id
#     # context = {
#     #     'id': id,
#     #     'user': c,
#     # }
#     return render(request, 'dashboard.html')


def Admin_Dashboard(request, admin_id):
    total_students = models.Student.objects.filter(admin_id=admin_id).count()
    total_courses = models.Course.objects.filter(admin_id=admin_id).count()
    total_enrollments = models.Enrollment.objects.filter(admin_id=admin_id).count()
    total_idcards = models.Idcard.objects.filter(enrollment__admin_id=admin_id).count()
    total_fees = models.Fees.objects.filter(admin_id=admin_id).count()
    total_fees_count = models.Fees.objects.filter(admin_id=admin_id).values(
        'student__student_id'  
    ).annotate(
        enroll_count=Count('receipt_no')
    ).count()
    total_certificates = models.Enrollment.objects.filter(admin_id=admin_id,payment_status="PAID").count()

    # Total counts
    total_students = models.Student.objects.filter(admin_id=admin_id).count()

    # Gender ratio for the chart
    registered_students = models.Student.objects.filter(admin_id=admin_id).count()
    enrolled_students = models.Enrollment.objects.filter(admin_id=admin_id)
    enrolled_students_count = enrolled_students.count()
    c = enrolled_students.filter(admin_id=admin_id,course_name_id = 1).count()
    print("enrolled students",c)
    top_courses = models.Enrollment.objects.filter(admin_id=admin_id).values(
        'course_name__course_name'   # Assuming ForeignKey is 'course_name' in Enrollment model
    ).annotate(
        enroll_count=Count('enroll_id')
    ).order_by('-enroll_count')[:3]  # Top 3 courses



    male_students = models.Student.objects.filter(admin_id=admin_id, gender='Male').count()
    female_students = models.Student.objects.filter(admin_id=admin_id, gender='Female').count()

    # Top students based on marks
    # top_students = models.Student.objects.filter(admin_id=admin_id).order_by('-marks')[:5]  # Top 5 students
    top_students = models.Enrollment.objects.filter(admin_id=admin_id)  # Top 5 students

    context = {
        'id': admin_id,
        'admin': models.Admin.objects.get(admin_id=admin_id),
        'total_students': total_students,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'total_idcards': total_idcards,
        'total_fees': total_fees_count,
        'total_certificates': total_certificates,
        'registered_students': registered_students,
        'enrolled_students': enrolled_students_count,
        'male_students': male_students,
        'female_students': female_students,
        'top_students': top_students,
        'top_courses': top_courses,
    }
    return render(request, 'admin_dashboard.html', context)


def Admin_logout(request, admin_id):
    c = models.Admin.objects.get(admin_id=admin_id)
    id = c.admin_id
    context = {
        'id': id,
        'user': c,
        'admin_id': admin_id,
    }
    a=models.Admin.objects.filter(admin_id=admin_id)
    if request.method == 'POST':
        return redirect('main_page')
    # context['a']= models.Admin.objects.filter(admin=admin_id)
    return render(request, 'admin_logout.html', context)  



def Member_logout(request,member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = c.admin_id
    context = {
        'id': id,
        'user': c,
        'admin_id': admin_id,
    }
    a=models.Admin.objects.filter(admin_id=admin_id)
    if request.method == 'POST':
        return redirect('main_page')
    # context['a']= models.Admin.objects.filter(admin=admin_id)
    return render(request, 'member_logout.html', context)  


def Member_List(request, admin_id):
    c = models.Admin.objects.get(admin_id=admin_id)
    id = c.admin_id
    members = models.Member.objects.filter(admin_id=admin_id).count()
    context = {
        'id': id,
        'admin': models.Admin.objects.get(admin_id=admin_id),
        'members': members,
        'admin_id': admin_id,
    }
    members = models.Member.objects.filter(admin_id=admin_id)
    context['members'] = members
    return render(request, 'member_list.html', context)



def Student(request, admin_id):
    c = models.Admin.objects.get(admin_id=admin_id)
    id = c.admin_id
    student = models.Student.objects.filter(admin_id=admin_id).count()
    context = {
        'id': id,
        'admin': models.Admin.objects.get(admin_id=admin_id),
        'student': student,
        'admin_id': admin_id,
    }
    student = models.Student.objects.filter(admin_id=admin_id)
    context['student'] = student
    return render(request, 'student.html', context)


def Course(request, admin_id):
    c = models.Admin.objects.get(admin_id=admin_id)
    id = c.admin_id
    course = models.Course.objects.filter(admin_id=admin_id).count()
    context = {
        'id': id,
        'admin': models.Admin.objects.get(admin_id=admin_id),
        'course': course,
        'admin_id': admin_id,
    }
    course = models.Course.objects.filter(admin_id=admin_id)
    context['course'] = course
    return render(request, 'course.html', context)


def Enrollment(request, admin_id):
    c = models.Admin.objects.get(admin_id=admin_id)
    id = c.admin_id
    enrollment = models.Enrollment.objects.filter(admin=admin_id)
    context = {
        'id': id,
        'admin': models.Admin.objects.get(admin_id=admin_id),
        'enrollment': enrollment,
        'admin_id': admin_id,
    }
    context['enrollment'] = enrollment
    return render(request, 'enrollment.html', context)


def IDCard(request, admin_id):
    c = models.Admin.objects.get(admin_id=admin_id)
    id = c.admin_id
    # enr = models.Enrollment.objects.filter(admin=admin_id)
    # print("enrollment",enr)
    idcard = models.Idcard.objects.filter(enrollment__admin=admin_id)
    context = {
        'id': id,
        'admin': models.Admin.objects.get(admin_id=admin_id),
        'idcard': idcard,
        # 'card_id': card_id,
    }
    context['idcard'] = idcard
    return render(request, 'idcard.html', context)


def Fee(request, admin_id):
    c = models.Admin.objects.get(admin_id=admin_id)
    id = c.admin_id
    fees = models.Fees.objects.filter(admin_id=admin_id).count()
    context = {
        'id': id,
        'admin': models.Admin.objects.get(admin_id=admin_id),
        'admin_id': admin_id,
    }
    fees = models.Fees.objects.filter(admin_id=admin_id)
    context['fees'] = fees
    return render(request, 'fee.html', context)


def Certificate(request, admin_id):
    c = models.Admin.objects.get(admin_id=admin_id)
    id = c.admin_id
    context = {
        'id': id,
        'admin': models.Admin.objects.get(admin_id=admin_id),
        'admin_id': admin_id,
    }
    certificate = models.Enrollment.objects.filter(admin=admin_id)
    context['certificate'] = certificate
    return render(request, 'certificate.html', context)


#-----------------------------------------------------------------------------------------------------------
#--------------------------------------------Member Dashboard----------------------------------#
#-----------------------------------------------------------------------------------------------------------

def Index(request, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    context = {
        'id': id,  # Ensure this is correctly set without trailing spaces
        'admin': c,
        'member': member,
    }
    return render(request, 'index.html', context)


def Course_registration(request, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    context = {
        'id': id,
        'admin': c,
        'member': member,
    }
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        duration = request.POST.get('duration')
        fees = request.POST.get('fees')

        a = models.Course.objects.filter(course_name=course_name,duration=duration,admin = admin_id,fees=fees).count()
        if a == 1:
            context['error'] = "Course already exists!!"
            return render(request, 'course_registration.html', context)
        else:
            admin_instance = models.Admin.objects.get(admin_id=admin_id)  # Retrieve the Admin instance
            course = models.Course.objects.create(
                course_name=course_name,
                duration=duration,
                admin = admin_instance,  # Assign the Admin instance to the course
                fees=fees
            )
            course.save()
            course = models.Course.objects.filter(admin = admin_id)
            context['course'] = course
            return render(request, 'course_list.html', context)
    return render(request, 'course_registration.html', context)

def Course_list(request, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    course = models.Course.objects.filter(admin = admin_id)
    context = {
        'id': id,
        'admin': c,
        'member': member,
        'course': course
    }
    course = models.Course.objects.filter(admin = admin_id)
    context['course'] = course
    return render(request, 'course_list.html', context)

def Course_delete(request, course_id, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    course = models.Course.objects.get(course_id=course_id)
    context = {
        'id': id,
        'admin': c,
        'member': member,
        'course': course,
    }
    if request.method == 'POST':
        course = models.Course.objects.filter(course_id = course_id)
        course.delete()
        context['course'] = models.Course.objects.filter(admin =  admin_id)
        return render(request, 'course_list.html', context)
    return render(request, 'course_delete.html', context)

def Course_edit(request, member_id, course_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    cour= models.Course.objects.get(course_id=course_id)
    context = {
        'id': id,
        'admin': c,
        'member': member,
        'course':cour,
        'course_id':course_id
    }
    # course = models.Course.objects.all()
    # context['course'] = course
    if request.method == 'POST':
        course_name = request.POST.get('course_name')
        course_id = request.POST.get('course_id')
        fees = request.POST.get('fees')
        duration = request.POST.get('duration')

        if course_name:
            cour.course_name = course_name
        if course_id:
            cour.course_id = course_id
        if duration:
            cour.duration = duration
            e = models.Enrollment.objects.filter(course_name = cour)
            if e.exists():
                for enrollment in e:
                    start_date = enrollment.start_date
                    print("start date",start_date)
                    print("start Date type",type(start_date))
                    end_date = add_months(enrollment.start_date.strftime('%Y-%m-%d'), cour.duration)
                    enrollment.end_date = datetime.strptime(end_date , '%Y-%m-%d').date()
                    enrollment.save()
        if fees:
            cour.fees = fees
        cour.save()
        course = models.Course.objects.filter(admin = admin_id)
        context['course'] = course
        return render(request, 'course_list.html', context)
    return render(request, 'course_edit.html', context)

def Enrollment_registration(request, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    course = models.Course.objects.all()
    student = models.Student.objects.all()

    context = {
        'id': id,
        'admin': c,
        'member': member,
        'course': course,
        'student': student,
    }
    if request.method == 'POST':
    #    enroll_id=request.POST.get('enroll_id')  # Fixed: Removed trailing comma
       student_id=request.POST.get('student_id')
       course_name=request.POST.get('course_name')
       admission_date=request.POST.get('admission_date')
       start_date=request.POST.get('start_date')
       print(course_name)

       a = models.Enrollment.objects.filter(student_id=student_id,course_name=course_name).count()
       if a == 1:
            context['error'] = "Enrollment already exist!!"
            return render(request, 'enrollment_registration.html', context)
       else:
            stu = models.Student.objects.get(student_id=student_id)
            cour = models.Course.objects.get(course_id=course_name)
            admin_instance = models.Admin.objects.get(admin_id=admin_id)
            print("__________________date_____________",admission_date)
            date_obj = datetime.strptime(admission_date, "%Y-%m-%d").date()  # Convert to date object
            y = date_obj.year  # Extract year
            m = date_obj.month  # Extract year
            year = y % 100
            print(type(year))
            print(type(m))
            Y = year * 100000000000
            M = m * 1000000000
            course_name = int(course_name)
            student_id = int(student_id)
            A = admin_id * 1000000
            C = course_name * 1000
            S = student_id
            enrollment_number = Y + M + A + C + S
            
            months_to_add = cour.duration  # Duration in months

            calculated_date = add_months(start_date, months_to_add)

            # if calculated_date:
            #     print("Calculated date:", calculated_date)
            # else:
            #     print("Invalid date format. Please use YYYY-MM-DD.")

            # Check if student is already enrolled in this course
            existing_enrollment = models.Enrollment.objects.filter(
            student_id=student_id,
            course_name=course_name
            ).first()
            if existing_enrollment:
                return render(request, 'enrollment_registration.html')
            
            enrollment = models.Enrollment.objects.create(
                student_id=stu,
                course_name=cour,
                admission_date=admission_date,
                start_date=start_date,
                enrollment_number=enrollment_number,
                admin = admin_instance,  # Assign the Admin instance to the enrollment
                end_date=calculated_date,
                # payment_status = 'PENDING',
            )
            enrollment.save()
            enrollment = models.Enrollment.objects.filter(admin_id = admin_id)
            context['enrollment'] = enrollment
            return render(request, 'enrollment_list.html', context)
    return render(request, 'enrollment_registration.html', context)

def Enrollment_update(request, enroll_id, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    enrollment=models.Enrollment.objects.get(enroll_id=enroll_id)
    course=models.Course.objects.all()
    context = {
        'id': id,
        'admin': c,
        'member':member,
        'course': course,
        'enrollment': enrollment,
        'enroll_id': enroll_id,
    }
    if request.method =='POST':
       course_name=request.POST.get('course_name')
    # else:
    #    cour = models.Course.objects.get(course_name=course_name)

       if course_name:
           cour = models.Course.objects.get(course_name=course_name)
           enrollment.course_name = cour
              
       enrollment.save()
       enrollment=models.Enrollment.objects.filter(admin=admin_id)
       context['enrollment']= enrollment
       return render(request, 'enrollment_list.html', context)
    return render(request, 'enrollment_update.html', context)

def Enrollment_list(request, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    # enrollment = models.Enrollment.objects.filter(admin = admin_id)
    enrollment = models.Enrollment.objects.filter(admin=admin_id)
    
    # Calculate fee status for each enrollment
    for enroll in enrollment:
        total_paid = 0
        fee_payments = models.Fees.objects.filter(enrollment_id=enroll.enroll_id)
        for fee in fee_payments:
            total_paid += fee.paid_amount
        print("total paid amount________________________________", total_paid)
        # Update payment status based on total paid amount
        if total_paid >= enroll.course_name.fees:
            enroll.payment_status = 'PAID'
        elif total_paid > 0:
            enroll.payment_status = 'PARTIAL'
        else:
            enroll.payment_status = 'PENDING'
            
        enroll.total_paid = total_paid
        enroll.pending_amount = enroll.course_name.fees - total_paid
        enroll.save()  # Save the updated payment status

    context = {
        'id': id,
        'admin': c,
        'member':member,
    }
    enrollment = models.Enrollment.objects.filter(admin = admin_id)
    context['enrollment'] = enrollment
    return render(request, 'enrollment_list.html', context)

def Enrollment_delete(request, member_id,enroll_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    enrollment = models.Enrollment.objects.get(enroll_id=enroll_id)
    context = {
        'id': id,
        'admin': c,
        'member': member,
        'enrollment': enrollment,
    }
    if request.method == 'POST':

        enrollment = models.Enrollment.objects.filter(enroll_id=enroll_id)
        enrollment.delete()
        context['enrollment'] = models.Enrollment.objects.filter(admin = admin_id)
        return render(request, 'enrollment_list.html', context)
    return render(request, 'delete_enrollment.html', context)

# def Generate_idcard(request, member_id):
    # admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    # member = models.Member.objects.get(member_id=member_id)
#     c = models.Admin.objects.get(admin_id=admin_id)
#     id = member.member_id
#     student = models.Student.objects.filter(admin=admin_id)
#     course = models.Course.objects.filter(admin=admin_id)
#     enroll_list = models.Enrollment.objects.filter(admin=admin_id)
#     context = {
#         'id': id,
#         'user': c,
#         'student': student,
#         'course':course,
#         "enroll_list" : enroll_list,
#     }
#     if request.method == 'POST':
#         # student_name=request.POST.get('student_id')
#         # course_name=request.POST.get('course_id')
#         # card_id=request.POST.get('card_id')
#         # issue_date=request.POST.get('issue_date')

#         # a=models.Idcard.objects.filter(student_id=student_name).count()
#         # if a==1:
#         #     context['error'] = "idcard already exist!"
#         #     return render(request, 'generate_idcard.html',context)
#         # else:
#         #     admin_instance = models.Admin.objects.get(admin_id=admin_id)
#         #     stud = models.Student.objects.get(student_id=student_name)
#         #     cour = models.Course.objects.get(course_id=course_name)
#         #     idcard=models.Idcard.objects.create(
#         #         student_id=stud,
#         #         course_id=cour,
#         #         card_id=card_id,
#         #         issue_date=issue_date,
#         #         admin = admin_instance
#         #     )
#         #     idcard.save()
#         #     idcard = models.Idcard.objects.filter(admin = admin_id)
#         #     context['idcard'] = idcard
#         enroll_id = request.POST.get("enroll_id")
#         issue_date = request.POST.get("issue_date")
#         enroll = models.Enrollment.objects.get(enroll_id=enroll_id)
#         if models.Idcard.objects.filter(enrollment=enroll,issue_date=issue_date).exists():
#             context['error'] = "idcard already exist!"
#             return render(request, 'generate_idcard.html', context)
#         else:
#             idcard = models.Idcard.objects.create(
#                 enrollment=enroll,
#                 issue_date=issue_date,
#             )
#             idcard.save()
#             enrollments = models.Enrollment.objects.filter(admin=admin_id)  # Get all enrollments for admin
#             idcards = models.Idcard.objects.filter(enrollment__in=enrollments)  # Get idcards for those enrollments

#             context['idcard'] = idcards

#         return render(request, 'idcard_list.html',context) 

#     return render(request, 'generate_idcard.html', context)

# def Delete_idcard(request, card_id, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    context = {
        'id': id,
        'user': c,
    }
    idcard = models.Idcard.objects.filter(card_id = card_id)
    idcard.delete()
    context['idcard'] = models.Idcard.objects.filter(card_id = card_id) 
    return render(request, 'idcard_list.html', context)

# def Idcard_list(request, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    
    # def get_photo(self,obj):
    #     return obj.photo
    # get_photo.short_description = 'Photo'

    # def get_enroll_id(self,obj):
    #    return obj.enroll_id
    # get_enroll_id.short_description = 'Enrollment no'

    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    enrollments = models.Enrollment.objects.filter(admin=admin_id)  # Get all enrollments for admin
    idcard = models.Idcard.objects.filter(enrollment__in=enrollments)  # Get idcards for those enrollments
    context = {
        'id': id,
        'user': c,
        'idcard' : idcard
    }
    return render(request, 'idcard_list.html', context)

# def Idcard_update(request, card_id, member_id):
#     admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
#     member = models.Member.objects.get(member_id=member_id)
#     c = models.Admin.objects.get(admin_id=admin_id)
#     id = member.member_id
#     idcard = models.Idcard.objects.get(card_id = card_id)
#     context = {
#         'id': id,
#         'user': c,
#     }
#     if request.method == 'POST':
#         student_id = request.POST.get('student_id')
#         course_id = request.POST.get('course_id')

#         if student_id:
#             idcard.student_id = student_id
#         if course_id:
#             idcard.course_id = course_id
#         idcard.save()
#         idcard = models.Idcard.objects.filter(admin = admin_id)
#         context['idcard'] = idcard
#         return render(request, 'idcard_list,html', context)
#     return render(request, 'idcard_update.html', context)

def Student_registration(request, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    context = {
        'id': id,
        'admin': c,
        'member': member,
    }
    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        gender = request.POST.get('gender')
        # enrollment = request.POST.get('enrollment')
        address = request.POST.get('address')
        phone_no = request.POST.get('phone_no')
        email = request.POST.get('email')
        dob = request.POST.get('DOB')
        photo = request.FILES.get('photo')
        
        inc = models.Student.objects.filter(email=email).count()
        if inc == 1:
            context['error'] = "Student already exists!!"
            return render(request, 'student_registration.html', context)
        else:
            admin_instance = models.Admin.objects.get(admin_id=admin_id)  # Retrieve the Admin instance
            student = models.Student.objects.create(
                    # enrollment=enrollment, 
                    name=student_name,
                    gender=gender, 
                    address=address,
                    phone_no=phone_no,
                    email=email,
                    DOB=dob,
                    photo=photo,
                    admin=admin_instance  # Assign the Admin instance to the student
            )
            student.save()
            students = models.Student.objects.filter(admin = admin_id)
            context['students'] = students
        return render(request, 'student_list.html', context)
    return render(request, 'student_registration.html', context)

def student_delete(request, student_id, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    student = models.Student.objects.get(student_id=student_id)
    print("student",student)
    context = {
        'id': id,
        'admin': c,
        'member': member,
        'student': student,
    }
    if request.method == 'POST':
        student = models.Student.objects.filter(student_id=student_id)
        student.delete()
        context['students'] = models.Student.objects.filter(admin = admin_id)
        return render(request , 'student_list.html', context)
    return render(request, 'student_delete.html', context)


def Student_list(request, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    student = models.Student.objects.filter(admin = admin_id)
    context = {
        'id': id,
        'admin': c,
        'member': member,
        'student': student,
    }
    students = models.Student.objects.filter(admin = admin_id)
    context['students'] = students
    # for i in context['students']:
    #     print("year",i.DOB.strftime("%y"))
    return render(request, 'student_list.html', context)

def Student_update(request, student_id, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    student = models.Student.objects.get(student_id=student_id)
    context = {
        'id': id,
        'admin': c,
        'member': member,
        'student': student,
        'student_id': student_id,
    }
    if request.method == 'POST':
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        phone_no = request.POST.get('phone_number')
        email = request.POST.get('email')
        dob = request.POST.get('dob')
        if name:
            student.name = name
        if gender:
            student.gender = gender
        if address:
            student.address = address                                   
        if phone_no:
            student.phone_no = phone_no
        if email:
            student.email = email
        if dob:
            student.DOB = dob   
        student.save()
        students = models.Student.objects.filter(admin = admin_id)
        context['students'] = students
        return render(request, 'student_list.html', context)
    return render(request, 'student_update.html', context)

def Student_detail(request, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    context = {
        'id': id,
        'admin': c,
        'member': member,
    }
    return render(request, 'student_list.html', context)

def Main_page(request):
    admin_id = 1
    return render(request, 'main_page.html', {'admin_id': admin_id})




def Student_verification(request):
    # c = models.Admin.objects.get(admin_id=admin_id)
    # id = member.member_id
    # context = {
    #     'id': id,
    #     'user': c,
    # }
    # verification = models.Student.objects.filter(admin = admin_id)
    # context['verification'] = verification
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        dob = request.POST.get('dob')

        inc = models.Student.objects.filter(student_id = student_id, DOB = dob).exists()
        if inc:
            context = {
                'success': 'Student Verified!'
            }
            return render(request, 'student_verification.html', context)
        else:
            context = {
                'error': 'Student not found!'
            }
            return render(request, 'student_verification.html', context)
    return render(request, 'student_verification.html')


# def Student_verification_qr(request):
#     return render(request, 'student_verification_qr.html')


def Certificate_generate(request, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    context = {
        'id': id,
        'admin': c,
        'member': member,
    }
    # if request.method == 'POST':
    #     student_name = request.POST.get('student_name')
    #     course_name = request.POST.get('course_name')
    #     start_date = request.POST.get('start_date')
    #     end_date = request.POST.get('end_date')
    #     # certificate_number = request.POST.get('certificate_number')

    #     a = models.Enrollment.objects.filter(admin_id=admin_id).count()
    #     if a == 0:
    #         return render(request, 'certificate_generate.html', {'error': 'No enrollment found!'})
    #     else:
    #         admin_instance = models.Admin.objects.get(admin_id=admin_id)
    #         cerificate = models.Enrollment.objects.create(
    #             student_name=student_name,
    #             course_name=course_name,
    #             start_date=start_date,
    #             end_date=end_date,
    #             admin_id=admin_instance
    #         )
    #         cerificate.save()
    #         return render(request, 'certificate_generate.html', {'success': 'Certificate Generated!'})
    #     context['certificate'] = cerificate

    return render(request, 'certificate_generate.html', context)

def Certificate_generate_enroll(request, admin_id,enrollment_id):
    c = models.Admin.objects.get(admin_id=admin_id)
    id = c.admin_id
    date_of_today = datetime.now().date()
    print("date of today",date_of_today)
    enroll = models.Enrollment.objects.get(enroll_id=enrollment_id)
    context = {
        'id': id,
        'admin': c,
        'enroll': enroll,
        'date_of_today': date_of_today
    }
    
    return render(request, 'certificate_generate_enroll.html', context)


def Fee_Collection(request, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    student = models.Student.objects.all()
    course = models.Course.objects.all()
    enrollment = models.Enrollment.objects.all()
    
    # Add course_id, fees and total paid amount to each enrollment for the template
    enrollment_data = []
    for e in enrollment:
        # Calculate total paid amount for this enrollment
        total_paid = 0
        fee_payments = models.Fees.objects.filter(enrollment_id=e.enroll_id)
        for fee in fee_payments:
            total_paid += fee.paid_amount
            
        enrollment_data.append({
            'enroll_id': e.enroll_id,
            'student_name': e.student_id.name,
            'course_id': e.course_name.course_id,
            'course_fees': e.course_name.fees,
            'total_paid': total_paid
        })
    
    context = {
        'id': id,
        'admin': c, 
        'member': member, 
        'student': student,
        'course': course,
        'enrollment': enrollment,
        'enrollment_data': enrollment_data,
    }
    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        receipt_no = request.POST.get('receipt_no')
        enrollment_id = request.POST.get('enrollment_id')
        course_name = request.POST.get('course_name')
        total_amount = request.POST.get('total_amount')
        paid_amount = request.POST.get('paid_amount')
        payment_mode = request.POST.get('payment_mode')
        upi_id = request.POST.get('upi_id')
        bank_transfer_id = request.POST.get('bank_transfer_id')
        credit_card_number = request.POST.get('credit_card_number')
        debit_card_number = request.POST.get('debit_card_number')
        net_banking_id = request.POST.get('net_banking_id')
        received_date = request.POST.get('received_date')

        a = models.Fees.objects.filter(receipt_no=receipt_no).count()
        if a == 1:
            context['error'] = "Receipt number already exist!"
            return render(request, 'fee_collection.html', context)
        else:
            admin_instance = models.Admin.objects.get(admin_id = admin_id)
            stud = models.Student.objects.get(student_id = student_name)
            cour = models.Course.objects.get(course_id = course_name)
            enroll = models.Enrollment.objects.get(enroll_id = enrollment_id)
            
            # Calculate total paid amount (including this payment)
            fees = models.Fees.objects.filter(enrollment_id=enroll, course_name=cour)
            total_paid_amount = sum(fee.paid_amount for fee in fees) + Decimal(str(paid_amount))
            if not total_amount:
                total_amount = "0.00"
            if not paid_amount:
                paid_amount = "0.00"
            
            fees = models.Fees.objects.create(
                total_amount = total_amount,
                paid_amount = paid_amount,
                total_paid_amount = total_paid_amount,
                student = stud,
                receipt_no = receipt_no,
                enrollment_id = enroll,
                course_name = cour,
                payment_mode = payment_mode,
                upi_id = upi_id if payment_mode == '2' else None,
                bank_transfer_id = bank_transfer_id if payment_mode == '3' else None,
                credit_card_number = credit_card_number if payment_mode == '5' else None,
                debit_card_number = debit_card_number if payment_mode == '6' else None,
                net_banking_id = net_banking_id if payment_mode == '7' else None,
                received_date = received_date,
                admin = admin_instance
            )
            fees.save()
            fees = models.Fees.objects.filter(admin = admin_id)
            context['fees'] = fees
            return render(request, 'fee_list.html', context)
    return render(request, 'fee_collection.html', context)

# def Fee_Collection(request, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
#     c = models.Admin.objects.get(admin_id=admin_id)
#     id = member.member_id
#     student = models.Student.objects.all()
#     course = models.Course.objects.all()
#     enrollment = models.Enrollment.objects.all()
    
#     # Add course_id to each enrollment for the template
#     enrollment_data = []
#     for e in enrollment:
#         enrollment_data.append({
#             'enroll_id': e.enroll_id,
#             'student_name': e.student_id.name,
#             'course_id': e.course_name.course_id
#         })
    
#     context = {
#         'id': id,
#         'user': c,  
#         'student': student,
#         'course': course,
#         'enrollment': enrollment,
#         'enrollment_data': enrollment_data,
#     }
#     if request.method == 'POST':
#         student_name = request.POST.get('student_name')
#         receipt_no = request.POST.get('receipt_no')
#         enrollment_id = request.POST.get('enrollment_id')
#         course_name = request.POST.get('course_name')
#         total_amount = request.POST.get('total_amount')
#         paid_amount = request.POST.get('paid_amount')
#         payment_mode = request.POST.get('payment_mode')
#         upi_id = request.POST.get('upi_id')
#         bank_transfer_id = request.POST.get('bank_transfer_id')
#         credit_card_number = request.POST.get('credit_card_number')
#         debit_card_number = request.POST.get('debit_card_number')
#         net_banking_id = request.POST.get('net_banking_id')
#         received_date = request.POST.get('received_date')

#         a = models.Fees.objects.filter(receipt_no=receipt_no).count()
#         if a == 1:
#             context['error'] = "Receipt number already exist!"
#             return render(request, 'fee_collection.html', context)
#         else:
#             admin_instance = models.Admin.objects.get(admin_id = admin_id)
#             stud = models.Student.objects.get(student_id = student_name)
#             cour = models.Course.objects.get(course_id = course_name)
#             enroll = models.Enrollment.objects.get(enroll_id = enrollment_id)
            
#             # Calculate total paid amount (including this payment)
#             fees = models.Fees.objects.filter(enrollment_id=enroll, course_name=cour)
#             total_paid_amount = sum(fee.paid_amount for fee in fees) + Decimal(str(paid_amount))
#             if not total_amount:
#                 total_amount = "0.00"
#             if not paid_amount:
#                 paid_amount = "0.00"
            
#             fees = models.Fees.objects.create(
#                 total_amount = total_amount,
#                 paid_amount = paid_amount,
#                 total_paid_amount = total_paid_amount,
#                 student_name = stud.name,
#                 receipt_no = receipt_no,
#                 enrollment_id = enroll,
#                 course_name = cour,
#                 payment_mode = payment_mode,
#                 upi_id = upi_id if payment_mode == '2' else None,
#                 bank_transfer_id = bank_transfer_id if payment_mode == '3' else None,
#                 credit_card_number = credit_card_number if payment_mode == '5' else None,
#                 debit_card_number = debit_card_number if payment_mode == '6' else None,
#                 net_banking_id = net_banking_id if payment_mode == '7' else None,
#                 received_date = received_date,
#                 admin = admin_instance
#             )
#             fees.save()
#             fees = models.Fees.objects.filter(admin = admin_id)
#             context['fees'] = fees
#             return render(request, 'fee_list.html', context)
#     return render(request, 'fee_collection.html', context)



# def Fee_Collection(request, member_id):
#     c = models.Admin.objects.get(admin_id=admin_id)
#     id = member.member_id
#     student = models.Student.objects.all()
#     course = models.Course.objects.all()
#     enrollment = models.Enrollment.objects.all()
#     context = {
#         'id': id,
#         'user': c,  
#         'student': student,
#         'course': course,
#         'enrollment': enrollment, 
#         }
#     if request.method == 'POST':
#         # student_name = request.POST.get('student_name')
#         receipt_no = request.POST.get('receipt_no')
#         enrollment_id = request.POST.get('enrollment_id')
#         # course_name = request .POST.get('course_name')
#         total_amount = request.POST.get('total_amount')
#         paid_amount = request.POST.get('paid_amount')
#         total_paid_amount = request.POST.get('total_paid_amount')
#         payment_mode = request.POST.get('payment_mode')
#         received_date = request.POST.get('received_date')

#         a = models.Fees.objects.filter(receipt_no=receipt_no).count()
#         if a == 1:
#             context['errro'] = "Receipt number already exist!"
#             return render(request, 'fee_collection.html', context)
#         else:
#             admin_instance = models.Admin.objects.get(admin_id = admin_id)
#             # stud = models.Student.objects.get(student_id = student_name)
#             # cour = models.Course.objects.get(course_id = course_name)
#             enroll = models.Enrollment.objects.get(enroll_id = enrollment_id)
#             fees = models.Fees.objects.create(
#                 # student_name = stud.name,
#                 receipt_no = receipt_no,
#                 enrollment_id = enroll,
#                 # course_name = cour,
#                 total_amount =  total_amount,
#                 paid_amount = paid_amount,
#                 total_paid_amount = total_paid_amount,
#                 payment_mode = payment_mode,
#                 received_date = received_date,
#                 admin = admin_instance  # Assign the Admin instance to the fees
#             )
#             fees.save()
#             fees = models.Fees.objects.filter(admin = admin_id)
#             context['fees'] = fees
#             return render(request, 'fee_list.html', context)
#     return render(request, 'fee_Collection.html', context)

def Fee_list(request, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    context = {
        'id': id,
        'admin': c,
        'member': member,
    }
    fees = models.Fees.objects.filter(admin = admin_id)
    context['fees'] = fees
    return render(request, 'fee_list.html', context)

def Fee_update(request, receipt_no, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    fees = models.Fees.objects.get(receipt_no = receipt_no)
    context = {
        'id': id,
        'admin': c,
        'member': member,
        'fees': fees,
        'receipt_no': receipt_no,
    }
    if request.method == 'POST':
        student_name = request.POST.get('student_name')
        course_name = request.POST.get('course')
        total_amount = request.POST.get('total_amount')
        paid_amount = request.POST.get('paid_amount')
        total_paid_amount = request.POST.get('total_paid_amount')

        if student_name:
            fees.student_name = student_name
        if course_name:
            fees.course_name = course_name 
        if total_amount:
            fees.total_amount = total_amount
        if paid_amount:
            fees.paid_amount = paid_amount
        if total_paid_amount:
            fees.total_paid_amount = total_paid_amount 
        fees.save()
        fees = models.Fees.objects.filter(admin = admin_id)
        context['fees'] = fees
        return render(request, 'fee_list.html', context)
    return render(request, 'fee_update.html', context)


def Fee_delete(request, member_id, receipt_no):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    fees = models.Fees.objects.get(receipt_no=receipt_no)
    context = {
        'id': id,
        'admin': c, 
        'member': member, 
        'fees': fees,  
    }
    if request.method == 'POST':
        fees = models.Fees.objects.filter(receipt_no = receipt_no)
        fees.delete()
        context['fees'] = models.Fees.objects.filter(admin = admin_id)
        return render(request, 'fee_list.html', context)
    return render(request, 'fee_delete.html', context)




def download_fee_receipt(request, member_id, receipt_no):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    try:
        # Get the fee record
        fee = models.Fees.objects.get(receipt_no=receipt_no)
        student = fee.enrollment_id.student_id  # Get student details
        enrollment = fee.enrollment_id  # Get enrollment details
        
        # Generate PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="fee_receipt_{fee.receipt_no}.pdf"'

        # Create the PDF with A4 size
        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4  # Keep track of the page size
        
        # Add border to the page
        p.rect(30, 30, width-60, height-60)
        
        # Add CTF logo
        try:
            logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'cft_logo.jpg')
            if not os.path.exists(logo_path):
                logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'image.jpg')
            if os.path.exists(logo_path):
                p.drawImage(logo_path, 50, height-120, width=80, height=80)  # Increased size from 50x50 to 80x80
            else:
                # Fallback to drawing a circle if logo not found
                p.setFillColor(colors.HexColor('#4B0082'))  # Purple color for CTF
                p.circle(90, height-80, 25, fill=1)  # Increased circle size from 15 to 25
                p.setFillColor(colors.white)
                p.setFont("Helvetica-Bold", 14)  # Increased font size from 10 to 14
                p.drawString(80, height-85, "CTF")  # Adjusted position for larger text
                p.setFillColor(colors.black)  # Reset color to black
        except Exception as e:
            print(f"Error loading logo: {e}")
            # Fallback to drawing a circle if logo not found
            p.setFillColor(colors.HexColor('#4B0082'))  # Purple color for CTF
            p.circle(90, height-80, 25, fill=1)  # Increased circle size from 15 to 25
            p.setFillColor(colors.white)
            p.setFont("Helvetica-Bold", 14)  # Increased font size from 10 to 14
            p.drawString(80, height-85, "CTF")  # Adjusted position for larger text
            p.setFillColor(colors.black)  # Reset color to black
        
        # Add header
        p.setFont("Helvetica-Bold", 16)
        # Calculate center position for the text
        text = "Computer Technology Foundation"
        text_width = p.stringWidth(text, "Helvetica-Bold", 16)
        x = (width - text_width) / 2
        p.drawString(x, height-100, text)
        
        # Add Receipt title
        p.setFont("Helvetica-Bold", 14)
        p.drawString(200, height-120, "Student Fees Receipt")
        
        # Add student details section with more information
        p.setFont("Helvetica-Bold", 12)
        y = height-160
        
        # Left side details
        p.drawString(50, y, "Student Details:")
        p.setFont("Helvetica", 11)
        y -= 20
        p.drawString(50, y, f"Name: {student.name}")
        y -= 20
        p.drawString(50, y, f"Enrollment No: {enrollment.enroll_id}")
        y -= 20
        p.drawString(50, y, f"Course: {fee.course_name}")
        y -= 20
        p.drawString(50, y, f"Contact: {student.phone_no}")
        y -= 20
        p.drawString(50, y, f"Email: {student.email}")
        
        # Right side details
        p.setFont("Helvetica-Bold", 12)
        p.drawString(380, height-160, "Receipt Details:")
        p.setFont("Helvetica", 11)
        y = height-180
        p.drawString(380, y, f"Receipt No: {fee.receipt_no}")
        y -= 20
        p.drawString(380, y, f"Date: {fee.received_date}")
        y -= 20
        p.drawString(380, y, f"Academic Year: 2024-2025")
        
        # Add fees details table
        y = height-320  # Adjusted y position after student details
        
        # Draw table border
        p.rect(50, y-150, 500, 180)  # Main table border
        
        # Table headers with background
        p.setFillColor(colors.HexColor('#f0f0f0'))
        p.rect(50, y, 500, 25, fill=1)  # Header background
        p.setFillColor(colors.black)
        
        p.setFont("Helvetica-Bold", 12)
        p.drawString(60, y+7, "Particulars")
        p.drawString(350, y+7, "Amount(Rs)")
        p.line(50, y, 550, y)  # Line below headers
        
        # Table content
        y -= 30
        p.setFont("Helvetica", 11)
        
        # Course Total Fee
        p.drawString(60, y, "Course Total Fee")
        p.drawString(350, y, f"{enrollment.course_name.fees:.2f}")
        p.line(50, y-5, 550, y-5)
        
        y -= 25
        # Previous Paid Amount
        previous_paid = fee.total_paid_amount - fee.paid_amount
        p.drawString(60, y, "Previous Paid Amount")
        p.drawString(350, y, f"{previous_paid:.2f}")
        p.line(50, y-5, 550, y-5)
        
        y -= 25
        # Current Paid Amount
        p.drawString(60, y, "Current Paid Amount")
        p.drawString(350, y, f"{fee.paid_amount:.2f}")
        p.line(50, y-5, 550, y-5)
        
        y -= 25
        # Total Paid Amount
        p.drawString(60, y, "Total Paid Amount")
        p.drawString(350, y, f"{fee.total_paid_amount:.2f}")
        p.line(50, y-5, 550, y-5)
        
        y -= 25
        # Remaining Amount
        remaining = enrollment.course_name.fees - fee.total_paid_amount
        p.drawString(60, y, "Remaining Amount")
        p.drawString(350, y, f"{remaining:.2f}")
        
        # Payment details
        y -= 50
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Payment Details:")
        p.setFont("Helvetica", 11)
        y -= 20
        
        # Payment Mode
        payment_mode_text = {
            '1': 'CASH',
            '2': 'UPI',
            '3': 'Bank Transfer',
            '4': 'Cheque',
            '5': 'Credit Card',
            '6': 'Debit Card',
            '7': 'Net Banking'
        }
        p.drawString(50, y, f"Payment Mode: {payment_mode_text.get(fee.payment_mode, 'N/A')}")
        
        # Transaction Details based on payment mode
        y -= 20
        if fee.payment_mode == '2' and fee.upi_id:
            p.drawString(50, y, f"UPI ID: {fee.upi_id}")
        elif fee.payment_mode == '3' and fee.bank_transfer_id:
            p.drawString(50, y, f"Bank Transfer ID: {fee.bank_transfer_id}")
        elif fee.payment_mode == '5' and fee.credit_card_number:
            p.drawString(50, y, f"Credit Card Number: {fee.credit_card_number}")
        elif fee.payment_mode == '6' and fee.debit_card_number:
            p.drawString(50, y, f"Debit Card Number: {fee.debit_card_number}")
        elif fee.payment_mode == '7' and fee.net_banking_id:
            p.drawString(50, y, f"Net Banking ID: {fee.net_banking_id}")
            
        # Transaction Date
        y -= 20
        p.drawString(50, y, f"Transaction Date: {fee.received_date}")
        
        # Amount in words
        y -= 40
        p.drawString(50, y, "Amount in Words:")
        p.setFont("Helvetica-Bold", 11)
        amount_in_words = num2words(int(float(fee.paid_amount))).title() + " Rupees Only"
        p.drawString(150, y, amount_in_words)
        
        # Note and signature
        y -= 40
        p.setFont("Helvetica", 10)
        p.drawString(50, y, "Note: This is a computer generated receipt and does not require signature.")
        p.setFont("Helvetica-Bold", 11)
        p.drawString(380, y, "AUTHORISED SIGNATORY")
        
        p.save()
        return response
        
    except models.Fees.DoesNotExist:
        messages.error(request, "Fee record not found.")
        return redirect('fee_list', member_id=member_id)
    except Exception as e:
        messages.error(request, f"Error generating receipt: {str(e)}")
        return redirect('fee_list', member_id=member_id)

# def download_fee_receipt(request, member_id, receipt_no):
#     try:
#         # Get the fee record
#         fee = models.Fees.objects.get(receipt_no=receipt_no)
#         student = fee.enrollment_id.student_id  # Get student details
#         enrollment = fee.enrollment_id  # Get enrollment details
        
#         # Generate PDF
#         response = HttpResponse(content_type='application/pdf')
#         response['Content-Disposition'] = f'attachment; filename="fee_receipt_{fee.receipt_no}.pdf"'

#         # Create the PDF with A4 size
#         p = canvas.Canvas(response, pagesize=A4)
#         width, height = A4  # Keep track of the page size
        
#         # Add border to the page
#         p.rect(30, 30, width-60, height-60)
        
#         # Add CTF logo
#         try:
#             logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'cft_logo.jpg')
#             if not os.path.exists(logo_path):
#                 logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'cft_logo.jpg')
#             if os.path.exists(logo_path):
#                 p.drawImage(logo_path, 50, height-120, width=80, height=80)  # Increased size from 50x50 to 80x80
#             else:
#                 # Fallback to drawing a circle if logo not found
#                 p.setFillColor(colors.HexColor('#4B0082'))  # Purple color for CTF
#                 p.circle(90, height-80, 25, fill=1)  # Increased circle size from 15 to 25
#                 p.setFillColor(colors.white)
#                 p.setFont("Helvetica-Bold", 14)  # Increased font size from 10 to 14
#                 p.drawString(80, height-85, "CTF")  # Adjusted position for larger text
#                 p.setFillColor(colors.black)  # Reset color to black
#         except Exception as e:
#             print(f"Error loading logo: {e}")
#             # Fallback to drawing a circle if logo not found
#             p.setFillColor(colors.HexColor('#4B0082'))  # Purple color for CTF
#             p.circle(90, height-80, 25, fill=1)  # Increased circle size from 15 to 25
#             p.setFillColor(colors.white)
#             p.setFont("Helvetica-Bold", 14)  # Increased font size from 10 to 14
#             p.drawString(80, height-85, "CTF")  # Adjusted position for larger text
#             p.setFillColor(colors.black)  # Reset color to black
        
#         # Add header
#         p.setFont("Helvetica-Bold", 16)
#         # Calculate center position for the text
#         text = "Computer Technology Foundation"
#         text_width = p.stringWidth(text, "Helvetica-Bold", 16)
#         x = (width - text_width) / 2
#         p.drawString(x, height-100, text)
        
#         # Add Receipt title
#         p.setFont("Helvetica-Bold", 14)
#         p.drawString(200, height-120, "Student Fees Receipt")
        
#         # Add student details section with more information
#         p.setFont("Helvetica-Bold", 12)
#         y = height-160
        
#         # Left side details
#         p.drawString(50, y, "Student Details:")
#         p.setFont("Helvetica", 11)
#         y -= 20
#         p.drawString(50, y, f"Name: {student.name}")
#         y -= 20
#         p.drawString(50, y, f"Enrollment No: {enrollment.enroll_id}")
#         y -= 20
#         p.drawString(50, y, f"Course: {fee.course_name}")
#         y -= 20
#         p.drawString(50, y, f"Contact: {student.phone_no}")
#         y -= 20
#         p.drawString(50, y, f"Email: {student.email}")
        
#         # Right side details
#         p.setFont("Helvetica-Bold", 12)
#         p.drawString(380, height-160, "Receipt Details:")
#         p.setFont("Helvetica", 11)
#         y = height-180
#         p.drawString(380, y, f"Receipt No: {fee.receipt_no}")
#         y -= 20
#         p.drawString(380, y, f"Date: {fee.received_date}")
#         y -= 20
#         p.drawString(380, y, f"Academic Year: 2024-2025")
        
#         # Add fees details table
#         y = height-320  # Adjusted y position after student details
        
#         # Draw table border
#         p.rect(50, y-150, 500, 180)  # Main table border
        
#         # Table headers with background
#         p.setFillColor(colors.HexColor('#f0f0f0'))
#         p.rect(50, y, 500, 25, fill=1)  # Header background
#         p.setFillColor(colors.black)
        
#         p.setFont("Helvetica-Bold", 12)
#         p.drawString(60, y+7, "Particulars")
#         p.drawString(350, y+7, "Amount (₹)")
#         p.line(50, y, 550, y)  # Line below headers
        
#         # Table content
#         y -= 30
#         p.setFont("Helvetica", 11)
        
#         # Course Total Fee
#         p.drawString(60, y, "Course Total Fee")
#         p.drawString(350, y, f"{enrollment.fees:.2f}")
#         p.line(50, y-5, 550, y-5)
        
#         y -= 25
#         # Previous Paid Amount
#         previous_paid = fee.total_paid_amount - fee.paid_amount
#         p.drawString(60, y, "Previous Paid Amount")
#         p.drawString(350, y, f"{previous_paid:.2f}")
#         p.line(50, y-5, 550, y-5)
        
#         y -= 25
#         # Current Paid Amount
#         p.drawString(60, y, "Current Paid Amount")
#         p.drawString(350, y, f"{fee.paid_amount:.2f}")
#         p.line(50, y-5, 550, y-5)
        
#         y -= 25
#         # Total Paid Amount
#         p.drawString(60, y, "Total Paid Amount")
#         p.drawString(350, y, f"{fee.total_paid_amount:.2f}")
#         p.line(50, y-5, 550, y-5)
        
#         y -= 25
#         # Remaining Amount
#         remaining = enrollment.fees - fee.total_paid_amount
#         p.drawString(60, y, "Remaining Amount")
#         p.drawString(350, y, f"{remaining:.2f}")
        
#         # Payment details
#         y -= 50
#         p.setFont("Helvetica-Bold", 12)
#         p.drawString(50, y, "Payment Details:")
#         p.setFont("Helvetica", 11)
#         y -= 20
        
#         # Payment Mode
#         payment_mode_text = {
#             '1': 'CASH',
#             '2': 'UPI',
#             '3': 'Bank Transfer',
#             '4': 'Cheque',
#             '5': 'Credit Card',
#             '6': 'Debit Card',
#             '7': 'Net Banking'
#         }
#         p.drawString(50, y, f"Payment Mode: {payment_mode_text.get(fee.payment_mode, 'N/A')}")
        
#         # Transaction Details based on payment mode
#         y -= 20
#         if fee.payment_mode == '2' and fee.upi_id:
#             p.drawString(50, y, f"UPI ID: {fee.upi_id}")
#         elif fee.payment_mode == '3' and fee.bank_transfer_id:
#             p.drawString(50, y, f"Bank Transfer ID: {fee.bank_transfer_id}")
#         elif fee.payment_mode == '5' and fee.credit_card_number:
#             p.drawString(50, y, f"Credit Card Number: {fee.credit_card_number}")
#         elif fee.payment_mode == '6' and fee.debit_card_number:
#             p.drawString(50, y, f"Debit Card Number: {fee.debit_card_number}")
#         elif fee.payment_mode == '7' and fee.net_banking_id:
#             p.drawString(50, y, f"Net Banking ID: {fee.net_banking_id}")
            
#         # Transaction Date
#         y -= 20
#         p.drawString(50, y, f"Transaction Date: {fee.received_date}")
        
#         # Amount in words
#         y -= 40
#         p.drawString(50, y, "Amount in Words:")
#         p.setFont("Helvetica-Bold", 11)
#         amount_in_words = num2words(int(float(fee.paid_amount))).title() + " Rupees Only"
#         p.drawString(150, y, amount_in_words)
        
#         # Note and signature
#         y -= 40
#         p.setFont("Helvetica", 10)
#         p.drawString(50, y, "Note: This is a computer generated receipt and does not require signature.")
#         p.setFont("Helvetica-Bold", 11)
#         p.drawString(380, y, "AUTHORISED SIGNATORY")
        
#         p.save()
#         return response
        
#     except models.Fees.DoesNotExist:
#         messages.error(request, "Fee record not found.")
#         return redirect('fee_list', member_id=member_id)
#     except Exception as e:
#         messages.error(request, f"Error generating receipt: {str(e)}")
#         return redirect('fee_list', member_id=member_id)

def download_all_fee_receipts(request, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    try:
        # Get all fees for the admin
        fees = models.Fees.objects.filter(admin=admin_id)
        
        # Create a zip file
        import zipfile
        from io import BytesIO
        
        # Create a BytesIO object to store the zip file
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Generate each receipt and add to zip
            for fee in fees:
                # Create PDF for each receipt
                response = HttpResponse(content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="fee_receipt_{fee.receipt_no}.pdf"'
                
                # Create the PDF with A4 size
                p = canvas.Canvas(response, pagesize=A4)
                width, height = A4
                
                # Add border to the page
                p.rect(30, 30, width-60, height-60)
                
                # Add CTF logo on the left side
                p.setFillColor(colors.HexColor('#000080'))
                p.circle(80, height-100, 30, fill=1)
                p.setFillColor(colors.white)
                p.setFont("Helvetica-Bold", 16)
                p.drawString(70, height-105, "CTF")
                p.setFillColor(colors.black)
                
                # Add header
                p.setFont("Helvetica-Bold", 16)
                text = "Computer Technology Foundation"
                text_width = p.stringWidth(text, "Helvetica-Bold", 16)
                x = (width - text_width) / 2
                p.drawString(x, height-100, text)
                
                # Add Receipt title
                p.setFont("Helvetica-Bold", 14)
                p.drawString(200, height-120, "Student Fees Receipt")
                
                # Add student details
                student = fee.enrollment_id.student_id
                enrollment = fee.enrollment_id
                
                p.setFont("Helvetica-Bold", 12)
                y = height-160
                
                # Left side details
                p.drawString(50, y, "Student Details:")
                p.setFont("Helvetica", 11)
                y -= 20
                p.drawString(50, y, f"Name: {student.name}")
                y -= 20
                p.drawString(50, y, f"Enrollment No: {enrollment.enroll_id}")
                y -= 20
                p.drawString(50, y, f"Course: {fee.course_name}")
                y -= 20
                p.drawString(50, y, f"Contact: {student.phone_no}")
                y -= 20
                p.drawString(50, y, f"Email: {student.email}")
                
                # Right side details
                p.setFont("Helvetica-Bold", 12)
                p.drawString(380, height-160, "Receipt Details:")
                p.setFont("Helvetica", 11)
                y = height-180
                p.drawString(380, y, f"Receipt No: {fee.receipt_no}")
                y -= 20
                p.drawString(380, y, f"Date: {fee.received_date}")
                y -= 20
                p.drawString(380, y, f"Academic Year: 2024-2025")
                
                # Add fees details table
                y = height-320
                
                # Draw table border
                p.rect(50, y-150, 500, 180)
                
                # Table headers with background
                p.setFillColor(colors.HexColor('#f0f0f0'))
                p.rect(50, y, 500, 25, fill=1)
                p.setFillColor(colors.black)
                
                p.setFont("Helvetica-Bold", 12)
                p.drawString(60, y+7, "Particulars")
                p.drawString(350, y+7, "Amount (₹)")
                p.line(50, y, 550, y)
                
                # Table content
                y -= 30
                p.setFont("Helvetica", 11)
                
                # Course Total Fee
                p.drawString(60, y, "Course Total Fee")
                p.drawString(350, y, f"{enrollment.fees:.2f}")
                p.line(50, y-5, 550, y-5)
                
                y -= 25
                # Previous Paid Amount
                previous_paid = fee.total_paid_amount - fee.paid_amount
                p.drawString(60, y, "Previous Paid Amount")
                p.drawString(350, y, f"{previous_paid:.2f}")
                p.line(50, y-5, 550, y-5)
                
                y -= 25
                # Current Paid Amount
                p.drawString(60, y, "Current Paid Amount")
                p.drawString(350, y, f"{fee.paid_amount:.2f}")
                p.line(50, y-5, 550, y-5)
                
                y -= 25
                # Total Paid Amount
                p.drawString(60, y, "Total Paid Amount")
                p.drawString(350, y, f"{fee.total_paid_amount:.2f}")
                p.line(50, y-5, 550, y-5)
                
                y -= 25
                # Remaining Amount
                remaining = enrollment.fees - fee.total_paid_amount
                p.drawString(60, y, "Remaining Amount")
                p.drawString(350, y, f"{remaining:.2f}")
                
                # Payment details
                y -= 50
                p.setFont("Helvetica-Bold", 12)
                p.drawString(50, y, "Payment Details:")
                p.setFont("Helvetica", 11)
                y -= 20
                
                # Payment Mode
                payment_mode_text = {
                    '1': 'CASH',
                    '2': 'UPI',
                    '3': 'Bank Transfer',
                    '4': 'Cheque',
                    '5': 'Credit Card',
                    '6': 'Debit Card',
                    '7': 'Net Banking'
                }
                p.drawString(50, y, f"Payment Mode: {payment_mode_text.get(fee.payment_mode, 'N/A')}")
                
                # Transaction Details based on payment mode
                y -= 20
                if fee.payment_mode == '2' and fee.upi_id:
                    p.drawString(50, y, f"UPI ID: {fee.upi_id}")
                elif fee.payment_mode == '3' and fee.bank_transfer_id:
                    p.drawString(50, y, f"Bank Transfer ID: {fee.bank_transfer_id}")
                elif fee.payment_mode == '5' and fee.credit_card_number:
                    p.drawString(50, y, f"Credit Card Number: {fee.credit_card_number}")
                elif fee.payment_mode == '6' and fee.debit_card_number:
                    p.drawString(50, y, f"Debit Card Number: {fee.debit_card_number}")
                elif fee.payment_mode == '7' and fee.net_banking_id:
                    p.drawString(50, y, f"Net Banking ID: {fee.net_banking_id}")
                    
                # Transaction Date
                y -= 20
                p.drawString(50, y, f"Transaction Date: {fee.received_date}")
                
                # Amount in words
                y -= 40
                p.drawString(50, y, "Amount in Words:")
                p.setFont("Helvetica-Bold", 11)
                amount_in_words = num2words(int(float(fee.paid_amount))).title() + " Rupees Only"
                p.drawString(150, y, amount_in_words)
                
                # Note and signature
                y -= 40
                p.setFont("Helvetica", 10)
                p.drawString(50, y, "Note: This is a computer generated receipt and does not require signature.")
                p.setFont("Helvetica-Bold", 11)
                p.drawString(380, y, "AUTHORISED SIGNATORY")
                
                p.save()
                
                # Add the PDF to the zip file
                zip_file.writestr(f"fee_receipt_{fee.receipt_no}.pdf", response.getvalue())
        
        # Create the final response
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="all_fee_receipts.zip"'
        return response
        
    except Exception as e:
        messages.error(request, f"Error generating receipts: {str(e)}")
        return redirect('fee_list', member_id=member_id)

# def download_idcard(request, member_id, card_id):
#     # Get the ID card instance
#     idcard = models.Idcard.objects.get(card_id=card_id)
    
#     # Generate PDF
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="idcard_{idcard.student_id.student_id}.pdf"'

#     # Create the PDF
#     p = canvas.Canvas(response, pagesize=(350, 200))
    
#     # Add CTF logo
#     try:
#         logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'cft_logo.jpg')
#         if not os.path.exists(logo_path):
#             logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'cft_logo.jpg')
#         if os.path.exists(logo_path):
#             p.drawImage(logo_path, 15, 140, width=80, height=80)  # Increased size from 50x50 to 80x80
#         else:
#             # Fallback to drawing a circle if logo not found
#             p.setFillColor(colors.HexColor('#4B0082'))  # Purple color for CTF
#             p.circle(55, 180, 25, fill=1)  # Increased circle size from 15 to 25
#             p.setFillColor(colors.white)
#             p.setFont("Helvetica-Bold", 14)  # Increased font size from 10 to 14
#             p.drawString(45, 175, "CTF")  # Adjusted position for larger text
#             p.setFillColor(colors.black)  # Reset color to black
#     except Exception as e:
#         print(f"Error loading logo: {e}")
#         # Fallback to drawing a circle if logo not found
#         p.setFillColor(colors.HexColor('#4B0082'))  # Purple color for CTF
#         p.circle(55, 180, 25, fill=1)  # Increased circle size from 15 to 25
#         p.setFillColor(colors.white)
#         p.setFont("Helvetica-Bold", 14)  # Increased font size from 10 to 14
#         p.drawString(45, 175, "CTF")  # Adjusted position for larger text
#         p.setFillColor(colors.black)  # Reset color to black
    
#     # Add college name
#     p.setFont("Helvetica-Bold", 12)
#     p.drawString(110, 170, "Computer Technology Foundation")  # Moved right to accommodate larger logo
#     p.setFont("Helvetica", 8)
#     p.drawString(110, 155, "Regd No E-38007")
#     p.drawString(110, 145, "ctfglobal.in")

#     # Add student details
#     p.setFont("Helvetica-Bold", 16)  # Increased font size to match HTML
#     p.drawString(20, 100, f"{idcard.student_id.name}")
#     p.setFont("Helvetica", 12)  # Adjusted font size for course
#     p.drawString(20, 80, f"Course: {idcard.course_id.course_name}")
#     p.drawString(20, 65, f"Enrollment ID: {idcard.student_id.student_id}")

#     # Add student photo with increased size
#     if idcard.student_id.photo:
#         try:
#             photo_path = idcard.student_id.photo.path
#             if os.path.exists(photo_path):
#                 p.drawImage(photo_path, 250, 70, width=90, height=90)
#         except Exception as e:
#             print(f"Error loading photo: {e}")

#     # Add validity
#     p.setFont("Helvetica", 8)
#     p.drawString(20, 10, f"Valid up to June 2025")

#     # Add Director signature
#     p.drawString(250, 25, "Director")
#     p.drawString(250, 15, "Hemang Raval")

#     p.save()
    
#     return response



# def download_idcard(request, member_id, card_id):
#     try:
#         # Get ID card instance
#         idcard = models.Idcard.objects.get(card_id=card_id)
        
#         # Generate PDF
#         response = HttpResponse(content_type='application/pdf')
#         response['Content-Disposition'] = f'attachment; filename="idcard_{idcard.enrollment.student_id.student_id}.pdf"'
        
#         # Create the PDF
#         p = canvas.Canvas(response, pagesize=(350, 200))
        
#         # Add CTF logo
#         try:
#             logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'cft_logo.jpg')
#             if not os.path.exists(logo_path):
#                 logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'cft_logo.jpg')
#             if os.path.exists(logo_path):
#                 p.drawImage(logo_path, 15, 140, width=80, height=80)
#             else:
#                 p.setFillColor(colors.HexColor('#4B0082'))
#                 p.circle(55, 180, 25, fill=1)
#                 p.setFillColor(colors.white)
#                 p.setFont("Helvetica-Bold", 14)
#                 p.drawString(45, 175, "CTF")
#                 p.setFillColor(colors.black)
#         except Exception as e:
#             print(f"Error loading logo: {e}")
#             p.setFillColor(colors.HexColor('#4B0082'))
#             p.circle(55, 180, 25, fill=1)
#             p.setFillColor(colors.white)
#             p.setFont("Helvetica-Bold", 14)
#             p.drawString(45, 175, "CTF")
#             p.setFillColor(colors.black)
        
#         # Add college name
#         p.setFont("Helvetica-Bold", 12)
#         p.drawString(110, 170, "Computer Technology Foundation")
#         p.setFont("Helvetica", 8)
#         p.drawString(110, 155, "Regd No E-38007")
#         p.drawString(110, 145, "ctfglobal.in")
        
#         # Add student details
#         p.setFont("Helvetica-Bold", 16)
#         p.drawString(20, 100, f"{idcard.enrollment.student_id.name}")
#         p.setFont("Helvetica", 12)
#         p.drawString(20, 80, f"Course: {idcard.enrollment.course_name.course_name}")
#         p.drawString(20, 65, f"Enrollment ID: {idcard.enrollment.enrollment_number}")
        
#         # Add student photo
#         if idcard.enrollment.student_id.photo:
#             try:
#                 photo_path = idcard.enrollment.student_id.photo.path
#                 if os.path.exists(photo_path):
#                     p.drawImage(photo_path, 250, 70, width=90, height=90)
#             except Exception as e:
#                 print(f"Error loading photo: {e}")
        
#         # Add validity
#         p.setFont("Helvetica", 8)
#         p.drawString(20, 10, f"Valid up to June 2025")
        
#         # Add Director signature
#         p.drawString(250, 25, "Director")
#         p.drawString(250, 15, "Hemang Raval")
        
#         p.save()
#         return response
        
#     except models.Idcard.DoesNotExist:
#         return redirect('idcard_list', member_id=member_id)
#     except Exception as e:
#         print(f"Error generating ID card: {str(e)}")
#         return redirect('idcard_list', member_id=member_id)


# def Generate_idcard(request, member_id):
#     try:
#         c = models.Admin.objects.get(admin_id=admin_id)
#         enroll_list = models.Enrollment.objects.all()
#         id = member.member_id
#         context ={
#             'id': id,
#             'user': c,
#             'enroll_list': enroll_list,

#         }
        
#         if request.method == 'POST':
#             enroll_id = request.POST.get('enroll_id')
#             issue_date = request.POST.get('issue_date')
            
#             try:
#                 enrollment = models.Enrollment.objects.get(enroll_id=enroll_id)
                
#                 # Check if ID card already exists for this student
#                 if models.Idcard.objects.filter(enrollment=enrollment).exists():
#                     messages.error(request, 'ID card already exists for this student.')
#                     return render(request, 'idcard_list.html', context)
                
#                 # Create ID card record
#                 idcard = models.Idcard.objects.create(
#                     enrollment=enrollment,
#                     issue_date=issue_date
#                 )
#                 idcard.save()
#                 # Generate PDF
#                 response = HttpResponse(content_type='application/pdf')
#                 response['Content-Disposition'] = f'attachment; filename="idcard_{enrollment.enrollment_number}.pdf"'
                
#                 # Create PDF
#                 p = canvas.Canvas(response)
                
#                 # Add logo
#                 logo_path = os.path.join(settings.MEDIA_ROOT, 'logo.png')
#                 if os.path.exists(logo_path):
#                     p.drawImage(logo_path, 50, 700, width=100, height=100)
                
#                 # Add student details
#                 p.setFont("Helvetica-Bold", 16)
#                 p.drawString(200, 750, "ID CARD")
#                 p.setFont("Helvetica", 12)
#                 p.drawString(50, 650, f"Name: {enrollment.student_id.name}")
#                 p.drawString(50, 600, f"Course: {enrollment.course_name.course_name}")
#                 p.drawString(50, 550, f"Enrollment ID: {enrollment.enrollment_number}")
#                 p.drawString(50, 500, f"Issue Date: {issue_date}")
                
#                 # Add QR code
#                 qr = qrcode.QRCode(version=1, box_size=10, border=5)
#                 qr.add_data(f"ID Card Verification\nName: {enrollment.student_id.name}\nEnrollment: {enrollment.enrollment_number}")
#                 qr.make(fit=True)
#                 qr_img = qr.make_image(fill_color="black", back_color="white")
                
#                 # Save QR code temporarily
#                 qr_path = os.path.join(settings.MEDIA_ROOT, 'temp_qr.png')
#                 qr_img.save(qr_path)
#                 p.drawImage(qr_path, 400, 600, width=100, height=100)
#                 os.remove(qr_path)  # Clean up temporary file
                
#                 p.showPage()
#                 p.save()
                
#                 messages.success(request, 'ID card generated successfully.')
#                 return response
                
#             except models.Enrollment.DoesNotExist:
#                 messages.error(request, 'Invalid enrollment selected.')
#                 return redirect('generate_idcard', member_id=member_id)
        
#         return render(request, 'generate_idcard.html', {'id': id, 'enroll_list': enroll_list})
        
#     except models.Admin.DoesNotExist:
#         messages.error(request, 'Admin not found.')
#         return redirect('login')
#     except Exception as e:
#         messages.error(request, f'Error generating ID card: {str(e)}')
#         return redirect('generate_idcard', context)
    

# def view_idcard(request, member_id, card_id):
#     try:
#         # Get admin instance
#         admin = models.Admin.objects.get(admin_id=admin_id)
        
#         # Get ID card details
#         idcard = models.Idcard.objects.get(card_id=card_id)
        
#         # Get student and course details through enrollment
#         student = idcard.enrollment.student_id
#         course = idcard.enrollment.course_name
        
#         # Generate QR code for verification
#         qr = qrcode.QRCode(
#             version=1,
#             error_correction=qrcode.constants.ERROR_CORRECT_L,
#             box_size=10,
#             border=4,
#         )
        
#         # Create QR data with student and course info
#         qr_data = f"""
# Student ID: {student.student_id}
# Name: {student.name}
# Course: {course.course_name}
# Issue Date: {idcard.issue_date}
# Valid Until: June 2025
# """
#         qr.add_data(qr_data)
#         qr.make(fit=True)
        
#         # Create QR code image
#         qr_image = qr.make_image(fill_color="black", back_color="white")
        
#         # Convert to base64
#         buffer = BytesIO()
#         qr_image.save(buffer, format="PNG")
#         qr_code = base64.b64encode(buffer.getvalue()).decode()
        
#         context = {
#             'id': admin_id,
#             'user': admin,
#             'idcard': idcard,
#             'student': student,
#             'course': course,
#             'qr_code': qr_code
#         }
        
#         return render(request, 'id_card_template.html', context)
        
#     except models.Admin.DoesNotExist:
#         return redirect('login')
#     except models.Idcard.DoesNotExist:
#         return redirect('idcard_list', member_id=member_id)
#     except Exception as e:
#         print(f"Error in view_idcard: {str(e)}")
#         return redirect('idcard_list', member_id=member_id)
    













def download_idcard(request, member_id, card_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    try:
        # Get ID card instance
        idcard = models.Idcard.objects.get(card_id=card_id)
        
        # Generate PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="idcard_{idcard.enrollment.student_id.student_id}.pdf"'
        
        # Create the PDF
        p = canvas.Canvas(response, pagesize=(350, 200))
        
        # Add CTF logo
        try:
            logo_path = os.path.join(settings.STATIC_ROOT, 'images', 'image.jpg')
            if not os.path.exists(logo_path):
                logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'image.jpg')
            if os.path.exists(logo_path):
                p.drawImage(logo_path, 15, 140, width=70, height=60)
            else:
                p.setFillColor(colors.HexColor('#4B0082'))
                p.circle(55, 180, 25, fill=1)
                p.setFillColor(colors.white)
                p.setFont("Helvetica-Bold", 14)
                p.drawString(45, 175, "CTF")
                p.setFillColor(colors.black)
        except Exception as e:
            print(f"Error loading logo: {e}")
            p.setFillColor(colors.HexColor('#4B0082'))
            p.circle(55, 180, 25, fill=1)
            p.setFillColor(colors.white)
            p.setFont("Helvetica-Bold", 14)
            p.drawString(45, 175, "CTF")
            p.setFillColor(colors.black)
        
        # Add college name
        p.setFont("Helvetica-Bold", 12)
        p.drawString(110, 170, "Computer Technology Foundation")
        p.setFont("Helvetica", 8)
        p.drawString(110, 155, "Regd No E-38007")
        p.drawString(110, 145, "ctfglobal.in")
        
        # Add student details
        p.setFont("Helvetica-Bold", 16)
        p.drawString(20, 100, f"{idcard.enrollment.student_id.name}")
        p.setFont("Helvetica", 12)
        p.drawString(20, 80, f"Course: {idcard.enrollment.course_name.course_name}")
        p.drawString(20, 65, f"Enrollment ID: {idcard.enrollment.enrollment_number}")
        
        # Add student photo
        if idcard.enrollment.student_id.photo:
            try:
                photo_path = idcard.enrollment.student_id.photo.path
                if os.path.exists(photo_path):
                    p.drawImage(photo_path, 250, 70, width=90, height=90)
            except Exception as e:
                print(f"Error loading photo: {e}")
        
        # Add validity
        p.setFont("Helvetica", 8)
        p.drawString(20, 10, f"Valid up to June 2025")
        
        # Add Director signature
        p.drawString(250, 25, "Director")
        p.drawString(250, 15, "Hemang Raval")
        
        p.save()
        return response
        
    except models.Idcard.DoesNotExist:
        return redirect('idcard_list', member_id=member_id)
    except Exception as e:
        print(f"Error generating ID card: {str(e)}")
        return redirect('idcard_list', member_id=member_id)


def Delete_idcard(request, card_id, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    idcard = models.Idcard.objects.get(card_id=card_id)
    context = {
        'id': id,
        'admin': c,
        'member': member,
        'idcard': idcard,
    }
    if request.method == 'POST':

        idcard = models.Idcard.objects.filter(card_id = card_id)
        idcard.delete()
        context['idcard'] = models.Idcard.objects.filter(enrollment__admin = admin_id) 
        return render(request, 'idcard_list.html', context)
    return render(request, 'delete_idcard.html', context)

def Idcard_list(request, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    # enroll = models.Enrollment.objects.filter(admin = admin_id)
    # Get all idcards with related student and course information
    idcards = models.Idcard.objects.filter(enrollment__admin=admin_id).order_by('card_id')
    
    # Debug print to check data
    for card in idcards:
        print(f"Card ID: {card.card_id}")
        print(f"Student: {card.enrollment.student_id.name}")
        print(f"Course: {card.enrollment.course_name.course_name}")
        print(f"Photo URL: {card.enrollment.student_id.photo.url if card.enrollment.student_id.photo else 'No photo'}")
        print("---")
    
    context = {
        'id': id,
        'admin': c,
        'member': member,
        'idcard': idcards,
    }
    return render(request, 'idcard_list.html', context)

def Idcard_update(request, card_id, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    idcard = models.Idcard.objects.get(card_id = card_id)
    context = {
        'id': id,
        'admin': c,
        'member': member,
    }
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        course_id = request.POST.get('course_id')

        if student_id:
            idcard.student_id = student_id
        if course_id:
            idcard.course_id = course_id
        idcard.save()
        idcard = models.Idcard.objects.filter(admin = admin_id)
        context['idcard'] = idcard
        return render(request, 'idcard_list,html', context)
    return render(request, 'idcard_update.html', context)


def view_idcard(request, member_id, card_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    try:
        # Get admin instance
        admin = models.Admin.objects.get(admin_id=admin_id)
        
        # Get ID card details
        idcard = models.Idcard.objects.get(card_id=card_id)
        
        # Get student and course details through enrollment
        student = idcard.enrollment.student_id
        course = idcard.enrollment.course_name
        
        # Generate QR code for verification
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Create QR data with student and course info
        qr_data = f"""
Student ID: {student.student_id}
Name: {student.name}
Course: {course.course_name}
Issue Date: {idcard.issue_date}
Valid Until: June 2025
"""
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = BytesIO()
        qr_image.save(buffer, format="PNG")
        qr_code = base64.b64encode(buffer.getvalue()).decode()
        
        context = {
            'id': admin_id,
            'user': admin,
            'idcard': idcard,
            'student': student,
            'course': course,
            'qr_code': qr_code
        }
        
        return render(request, 'id_card_template.html', context)
        
    except models.Admin.DoesNotExist:
        return redirect('login')
    except models.Idcard.DoesNotExist:
        return redirect('idcard_list', member_id=member_id)
    except Exception as e:
        print(f"Error in view_idcard: {str(e)}")
        return redirect('idcard_list', member_id=member_id)
    

def Generate_idcard(request, member_id):
    admin_id = models.Member.objects.get(member_id=member_id).admin.admin_id
    member = models.Member.objects.get(member_id=member_id)
    
    c = models.Admin.objects.get(admin_id=admin_id)
    id = member.member_id
    enroll_list = models.Enrollment.objects.all()
    context = {
        'id': id,
        'admin': c,
        'member': member,
        'enroll_list': enroll_list,
    }
    print("_____________________request__________________________")
    print(request.method)
    if request.method == 'POST':
        enroll_id = request.POST.get('enroll_id')
        issue_date = request.POST.get('issue_date')
        if models.Idcard.objects.filter(enrollment=enroll_id).exists():
            context['error'] = 'ID card already exists for this student.'
            return render(request,'generate_idcard.html', context)
        else:
            idcard = models.Idcard.objects.create(
                    enrollment=models.Enrollment.objects.get(enroll_id=enroll_id),
                    issue_date=issue_date
                )
            idcard.save()
            context['idcard'] = models.Idcard.objects.filter(enrollment__admin=admin_id).order_by('card_id')
            return render(request, 'idcard_list.html',context)
            
            # try:
            #     enrollment = models.Enrollment.objects.get(enroll_id=enroll_id)
                
            #     # Check if ID card already exists for this student
            #     if models.Idcard.objects.filter(enrollment=enrollment).exists():
            #         messages.error(request, 'ID card already exists for this student.')
            #         return redirect('idcard_list', member_id=member_id)
                
            #     # Create ID card record
            #     idcard = models.Idcard.objects.create(
            #         enrollment=enrollment,
            #         issue_date=issue_date
            #     )
            #     # Generate PDF
            #     response = HttpResponse(content_type='application/pdf')
            #     response['Content-Disposition'] = f'attachment; filename="idcard_{enrollment.enrollment_number}.pdf"'
                
            #     # Create PDF
            #     p = canvas.Canvas(response)
                
            #     # Add logo
            #     logo_path = os.path.join(settings.MEDIA_ROOT, 'logo.png')
            #     if os.path.exists(logo_path):
            #         p.drawImage(logo_path, 50, 700, width=100, height=100)
                
            #     # Add student details
            #     p.setFont("Helvetica-Bold", 16)
            #     p.drawString(200, 750, "ID CARD")
            #     p.setFont("Helvetica", 12)
            #     p.drawString(50, 650, f"Name: {enrollment.student_id.name}")
            #     p.drawString(50, 600, f"Course: {enrollment.course_name.course_name}")
            #     p.drawString(50, 550, f"Enrollment ID: {enrollment.enrollment_number}")
            #     p.drawString(50, 500, f"Issue Date: {issue_date}")
                
            #     # Add QR code
            #     qr = qrcode.QRCode(version=1, box_size=10, border=5)
            #     qr.add_data(f"ID Card Verification\nName: {enrollment.student_id.name}\nEnrollment: {enrollment.enrollment_number}")
            #     qr.make(fit=True)
            #     qr_img = qr.make_image(fill_color="black", back_color="white")
                
            #     # Save QR code temporarily
            #     qr_path = os.path.join(settings.MEDIA_ROOT, 'temp_qr.png')
            #     qr_img.save(qr_path)
            #     p.drawImage(qr_path, 400, 600, width=100, height=100)
            #     os.remove(qr_path)  # Clean up temporary file
                
            #     p.showPage()
            #     p.save()
                
            #     messages.success(request, 'ID card generated successfully.')
            #     return response
                
            # except models.Enrollment.DoesNotExist:
            #     messages.error(request, 'Invalid enrollment selected.')
            #     return redirect('generate_idcard', member_id=member_id)
        
    return render(request, 'generate_idcard.html',context)
        
    