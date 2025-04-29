from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from myapp import views

urlpatterns = [
    path('student_registration/<int:member_id>', views.Student_registration, name='student_registration'),
    path('student_delete/<int:member_id>/<int:student_id>', views.student_delete, name='student_delete'),
    path('student_list/<int:member_id>', views.Student_list, name='student_list'),
    path('student_update/<int:member_id>/<int:student_id>', views.Student_update, name='student_update'),
    path('student_detail/<int:member_id>', views.Student_detail, name='student_detail'),
    path('generate_idcard/<int:member_id>', views.Generate_idcard, name='generate_idcard'),
    path('delete_idcard/<int:member_id>/<int:card_id>', views.Delete_idcard, name='delete_idcard'),
    path('idcard_list/<int:member_id>', views.Idcard_list, name='idcard_list'),
    path('idcard_update/<int:member_id>/<int:card_id>', views.Idcard_update, name='idcard_update'),
    path('enrollment_registration/<int:member_id>', views.Enrollment_registration, name='enrollment_registration'),
    path('enrollment_update/<int:member_id>/<int:enroll_id>', views.Enrollment_update, name='enrollment_update'),
    path('enrollment_list/<int:member_id>', views.Enrollment_list, name='enrollment_list'),
    path('enrollment_delete/<int:member_id>/<int:enroll_id>', views.Enrollment_delete, name='enrollment_delete'),
    path('course_registration/<int:member_id>', views.Course_registration, name='course_registration'),
    path('course_list/<int:member_id>', views.Course_list, name='course_list'),
    path('course_delete/<int:member_id>/<int:course_id>', views.Course_delete, name='course_delete'),  
    path('course_edit/<int:member_id>/<int:course_id>', views.Course_edit, name='course_edit'),
    path('fee_collection/<int:member_id>', views.Fee_Collection, name='fee_collection'),
    path('fee_list/<int:member_id>', views.Fee_list, name='fee_list'),
    path('fee_update/<int:member_id>/<int:receipt_no>', views.Fee_update, name='fee_update'),
    path('fee_delete/<int:member_id>/<int:receipt_no>', views.Fee_delete, name='fee_delete'),

    path('certificate_generate/<int:member_id>', views.Certificate_generate, name='certificate_generate'),
    path('certificate_generate/<int:admin_id>/<int:enrollment_id>', views.Certificate_generate_enroll, name='certificate_generate_enroll'),
    path('index/<int:member_id>', views.Index, name='index'),
    # path('student_verification_qr', views.Student_verification_qr, name='student_verification_qr'),
    path('download_fee_receipt/<int:member_id>/<int:receipt_no>/', views.download_fee_receipt, name='download_fee_receipt'),
    path('download_all_fee_receipts/<int:member_id>', views.download_all_fee_receipts, name='download_all_fee_receipts'),
    path('download_idcard/<int:member_id>/<str:card_id>/', views.download_idcard, name='download_idcard'),
    path('view_idcard/<int:member_id>/<int:card_id>/', views.view_idcard, name='view_idcard'),

    path('', views.Main_page, name='main_page'), 
    path('admin_login/', views.Admin_Login, name='admin_login'),
    path('member_login/', views.Member_Login, name='member_login'),
    path('admin_logout/<int:admin_id>', views.Admin_logout, name='admin_logout'),
    path('member_logout/<int:member_id>', views.Member_logout, name='member_logout'),
    path('student_verification', views.Student_verification, name='student_verification'),


    path('student/<int:admin_id>/', views.Student, name='student'),
    path('course/<int:admin_id>/', views.Course, name='course'),
    path('enrollment/<int:admin_id>/', views.Enrollment, name='enrollment'),
    path('idcard/<int:admin_id>', views.IDCard, name='idcard'),
    path('fee/<int:admin_id>/', views.Fee, name='fee'),
    path('certificate/<int:admin_id>/', views.Certificate, name='certificate'),
    path('member_register/<int:admin_id>', views.Member_Register, name='member_register'),
    path('member_list/<int:admin_id>', views.Member_List, name='member_list'),
    path('admin_register/', views.Admin_Register, name='admin_register'),
    path('admin_dashboard/<int:admin_id>', views.Admin_Dashboard, name='admin_dashboard'),






    
    

]
