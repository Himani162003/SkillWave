from django.db import models

# Create your models here.
    
class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True, verbose_name="ID")
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=10)
    name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.admin_id) +" " + self.name + " " + self.email
    
class Member(models.Model):
    member_id = models.AutoField(primary_key=True, verbose_name="ID")
    admin = models.ForeignKey(Admin, on_delete = models.CASCADE )
    member_name = models.CharField(max_length=50)
    member_email = models.EmailField(max_length=50)
    member_password = models.CharField(max_length=10)
    member_phone = models.CharField(max_length=10)
    date_of_joining = models.DateField()

    def __str__(self):
        return str(self.member_id) +" | " + self.member_name + " | " + str(self.admin.admin_id)



    
class Student(models.Model):
    student_id = models.AutoField(primary_key=True, verbose_name="ID")  # Fixed spelling: student_id → ID
    admin = models.ForeignKey(Admin, on_delete = models.CASCADE )
    # enrollment = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=10)
    email = models.CharField(max_length=50)
    DOB = models.DateField()
    photo = models.FileField(upload_to='static/images/student_photos/', null=True)  # Fixed max_length to 1
    # course= models.ManyToManyField("Course", through="Enrollment", related_name="students")
    marks = models.IntegerField(default=0)  # Assuming marks field exists
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])  # Add this field

    def __str__(self):
        return f"ID: {self.student_id}, Name: {self.name}, Address: {self.address}, Phone: {self.phone_no}, Email: {self.email}, DOB: {self.DOB}, Photo: {self.photo}"


class Course(models.Model):
    course_id = models.AutoField(verbose_name="course_id",primary_key=True)
    admin = models.ForeignKey(Admin, on_delete = models.CASCADE )
    course_name = models.CharField(max_length=30)
    duration = models.IntegerField(help_text="Duration in month")
    fees = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        return self.course_name


class Enrollment(models.Model):
    enroll_id = models.AutoField(primary_key=True)  # Fixed spelling: enorll_id → enroll_id
    enrollment_number = models.CharField(max_length=30,verbose_name="Enrollment Number")
    admin = models.ForeignKey(Admin, on_delete = models.CASCADE )
    student_id = models.ForeignKey(Student, verbose_name="name", on_delete=models.CASCADE, related_name="enrollments")
    course_name = models.ForeignKey(Course, verbose_name="course_name", on_delete=models.CASCADE, related_name="enrollments")
    admission_date = models.DateField()  # Fixed spelling: Addmission_date → admission_date
    start_date = models.DateField()
    end_date = models.DateField()
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pending_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)


    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('PARTIAL', 'Partial'),
    ]
    payment_status = models.CharField(max_length=10,choices=PAYMENT_STATUS_CHOICES,default='PENDING',verbose_name="Payment Status")

    def __str__(self):
        return f"Enrollment {self.enroll_id} - Student {self.student_id} in Course {self.course_name}"


class Idcard(models.Model):
    card_id = models.AutoField(primary_key=True)
    enrollment = models.ForeignKey(Enrollment,on_delete=models.CASCADE, null=False)
    # admin = models.ForeignKey(Admin, on_delete = models.CASCADE )
    # course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    # student_id = models.ForeignKey(Student, on_delete=models.CASCADE)
    issue_date = models.DateField()

    def __str__(self):
        # return self.card_id
        return f"ID: {self.card_id}, Student: {self.enrollment.student_id}, Course: {self.enrollment.course_name}"


# class Fees(models.Model):
#     student_name = models.CharField(max_length=50)
#     admin = models.ForeignKey(Admin, on_delete = models.CASCADE)
#     receipt_no = models.AutoField(primary_key=True)
#     enrollment_id = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='fee_payments')
#     course_name = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='fee_records')
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     # discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     # balance_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     total_paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     payment_mode = models.CharField(max_length=20)
#     received_date = models.DateField()
#     # created_at = models.DateTimeField()

# #     # class Meta:
# #     #     verbose_name = 'Fee'
# #     #     verbose_name_plural = 'Fees'

#     def _str_(self):
#         return f"Receipt: {self.student_name} - {self.receipt_no} - {self.enrollment_id} - {self.course_name} - {self.total_amount} - {self.paid_amount} - {self.total_paid_amount} - {self.payment_mode} - {self.received_date}"

class Fees(models.Model):
    PAYMENT_MODE_CHOICES = [
        ('1', 'Cash'),
        ('2', 'UPI'),
        ('3', 'Bank Transfer'),
        ('4', 'Cheque'),
        ('5', 'Credit Card'),
        ('6', 'Debit Card'),
        ('7', 'Net Banking'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    admin = models.ForeignKey(Admin, on_delete = models.CASCADE)
    receipt_no = models.AutoField(primary_key=True)
    enrollment_id = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='fee_payments')
    course_name = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='fee_records')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODE_CHOICES, default='1')
    upi_id = models.CharField(max_length=50, blank=True, null=True)
    bank_transfer_id = models.CharField(max_length=50, blank=True, null=True)
    credit_card_number = models.CharField(max_length=20, blank=True, null=True)
    debit_card_number = models.CharField(max_length=20, blank=True, null=True)
    net_banking_id = models.CharField(max_length=50, blank=True, null=True)
    received_date = models.DateField()

#     # class Meta:
#     #     verbose_name = 'Fee'
#     #     verbose_name_plural = 'Fees'

    def _str_(self):
        return f"Receipt: {self.student.name} - {self.receipt_no} - {self.enrollment_id} - {self.course_name} - {self.total_amount} - {self.paid_amount} - {self.total_paid_amount} - {self.payment_mode} - {self.received_date}"