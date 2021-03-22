from django.db import models


# Create your models here.
class books(models.Model):
    serial_no=models.AutoField
    accession_number =models.CharField(max_length=100, default="0")
    dates = models.DateField(blank=True, null=True)
    title = models.CharField(max_length=100, default="")
    author = models.CharField(max_length=100, default="")
    classification = models.CharField(max_length=100, default="")
    publisher = models.CharField(max_length=60, default="")
    category = models.CharField(max_length=100, default="")
    volume = models.CharField(max_length=100, default="")
    yearPublication = models.CharField(max_length=100, default="")
    no_pages =  models.CharField(max_length=100, default="0")
    purchased_from = models.CharField(max_length=100, default="")
    bill_no = models.CharField(max_length=100, default="")
    bill_date = models.DateField(blank=True, null=True)
    cost =models.CharField(max_length=100, default="0")
    edition = models.CharField(max_length=150, default="0")
    withdrawal_no = models.CharField(max_length=100, default="",blank=True)
    withdrawal_date = models.DateField(blank=True, null=True)
    copies = models.IntegerField(default=0)
    deleted = models.CharField(max_length=150, default="",blank=True)


    def __str__(self):
        return self.accession_number


class students(models.Model):
    serial_no = models.AutoField
    admission_no =models.CharField(max_length=100, default="0")
    dof_admission = models.DateField()
    roll_no = models.CharField(max_length=100, default="0")
    std_name =models.CharField(max_length=100, default="")
    gender =models.CharField(max_length=100, default="")
    dob = models.DateField()
    fname =models.CharField(max_length=100, default="")
    mname =models.CharField(max_length=100, default="")
    blood_group =models.CharField(max_length=100, default="NA")
    expiry_date = models.DateTimeField(blank=True, null=True)

    address1 =models.CharField(max_length=100, default="")

    city =models.CharField(max_length=100, default="")

    state =models.CharField(max_length=100, default="")
    email =models.CharField(max_length=100, default="")
    contact = models.IntegerField(default=0)

    remarks =models.CharField(max_length=100, default="no")
    deleted = models.CharField(max_length=150, default="no")
    no_books= models.IntegerField(default=0)
    def __str__(self):
        return self.roll_no


class employees(models.Model):
    serial_no = models.AutoField
    emp_id =models.CharField(max_length=100, default="0")
    dof_join = models.DateField(default="")
    emp_name =models.CharField(max_length=100, default="")
    gender =models.CharField(max_length=100, default="")
    dob = models.DateField()
    fname =models.CharField(max_length=100, default="")
    spouse_name =models.CharField(max_length=100, default="")
    email =models.CharField(max_length=100, default="")
    contact = models.IntegerField(default=0)

    address1 =models.CharField(max_length=100, default="")

    city =models.CharField(max_length=100, default="")

    state =models.CharField(max_length=100, default="")
    has_left =models.CharField(max_length=100, default="no")
    incharge =models.CharField(max_length=100, default="no")
    deleted = models.CharField(max_length=150, default="no")
    no_books = models.IntegerField(default=0)
    def __str__(self):
        return self.emp_id

class manage_books(models.Model):
    serial_id = models.AutoField
    accession_id =models.CharField(max_length=100, default="0")
    title = models.CharField(max_length=100, default="")
    student_id =models.CharField(max_length=100, default="",blank=True)
    std_name = models.CharField(max_length=100, default="",blank=True)
    emp_id =models.CharField(max_length=100, default="",blank=True)
    emp_name = models.CharField(max_length=100, default="",blank=True)
    issue_date = models.DateField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    fine = models.IntegerField()
    issued= models.CharField(max_length=100, default="yes")
    returned = models.CharField(max_length=100, default="no")
    def __str__(self):
        return self.accession_id

class newspaper(models.Model):
    serial_no=models.AutoField
    title = models.CharField(max_length=100, default="",blank=True)
    date_of_receipt = models.DateField(blank=True, null=True)
    volume =models.CharField(max_length=100, default="",blank=True)
    no1 =models.CharField(max_length=100, default="",blank=True)
    year =models.CharField(max_length=100, default="",blank=True)
    price = models.CharField(max_length=100, default="",blank=True)
    type = models.CharField(max_length=100, default="",blank=True)
    publisher = models.CharField(max_length=100, default="",blank=True)
    supplier = models.CharField(max_length=100, default="",blank=True)
    s_email =models.CharField(max_length=100, default="",blank=True)
    s_contact =models.CharField(max_length=100, default="",blank=True)
    language= models.CharField(max_length=100, default="",blank=True)
    frequency= models.CharField(max_length=100, default="",blank=True)
    issn_no =models.CharField(max_length=100, default="",blank=True)
    deleted = models.CharField(max_length=150, default="",blank=True)


    def __str__(self):
        return self.title

class bookbank(models.Model):
    serial_no=models.AutoField
    accession_number =models.CharField(max_length=100, default="0")
    dates = models.DateField(blank=True, null=True)
    title = models.CharField(max_length=100, default="")
    author = models.CharField(max_length=100, default="")
    classification = models.CharField(max_length=100, default="")
    publisher = models.CharField(max_length=60, default="")
    category = models.CharField(max_length=100, default="")
    volume = models.CharField(max_length=100, default="")
    yearPublication = models.CharField(max_length=100, default="")
    no_pages =  models.CharField(max_length=100, default="0")
    purchased_from = models.CharField(max_length=100, default="")
    bill_no = models.CharField(max_length=100, default="")
    bill_date = models.DateField(blank=True, null=True)
    cost = models.CharField(max_length=100, default="0")
    edition = models.CharField(max_length=150, default="0")
    withdrawal_no = models.CharField(max_length=100, default="",blank=True)
    withdrawal_date = models.DateField(blank=True, null=True)
    copies = models.IntegerField(default=0)
    deleted = models.CharField(max_length=150, default="",blank=True)


    def __str__(self):
        return self.accession_number

class manage_bookbank(models.Model):
    serial_id = models.AutoField
    accession_id =models.CharField(max_length=100, default="0")
    title = models.CharField(max_length=100, default="")
    student_id =models.CharField(max_length=100, default="")
    std_name = models.CharField(max_length=100, default="")
    emp_id =models.CharField(max_length=100, default="")
    emp_name = models.CharField(max_length=100, default="")
    issue_date = models.DateField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    fine = models.IntegerField()
    issued= models.CharField(max_length=100, default="yes")
    returned = models.CharField(max_length=100, default="no")
    def __str__(self):
        return self.accession_id



