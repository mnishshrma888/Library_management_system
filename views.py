import barcode
from barcode.writer import ImageWriter
from django.shortcuts import render, redirect
from django.http import HttpResponse
import pyzbar.pyzbar as pyzbar
import cv2
import requests
import datetime
import schedule
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import books, manage_books, students, employees, newspaper, bookbank, manage_bookbank
from django.db.models import Q, Count


# Create your views here.

def home(request):
    def notification():
        def msg(msg1, phn):
            msg2 = msg1
            phn_no = phn
            url = "https://www.fast2sms.com/dev/bulk"

            querystring = {
                "authorization": " C16QoaWfeOkvMsm7NJbhAqjzIXi40rpY9VxHUtgynFuwDELSPTzHLV2nRbi98caMtWqNUIyuemo417jQ ",
                "sender_id": "FSTSMS", "message": msg2, "language": "english", "route": "p", "numbers": phn_no}

            headers = {'cache-control': "no-cache"}

            response = requests.request("GET", url, headers=headers, params=querystring)

            print(response.text)

        ver2 = manage_books.objects.all()
        print(ver2)

        for i in ver2:
            ph = i.contact
            day = datetime.date.today()
            stored_day = i.return_date
            b = stored_day.day - day.day
            if b == 2:
                print("pending days are two")
                m = "Two days left to return book"

                msg(m, ph)
            elif b == 1:
                print("pending days are one")
                m = "One day left to return book"

                msg(m, ph)
            elif b == 0:
                print("today is last day")
                m = "Today is last day  to return book"

                msg(m, ph)
        for j in ver2:
            day = datetime.date.today()
            stored_day = j.return_date
            c = day.day - stored_day.day
            if c > 0:
                j.fine = int(c) * 5
                print(j.fine)
                j.save()
            else:
                j.fine = 0
                j.save()

    schedule.every().day.at("10:00").do(notification)
    return render(request, 'login.html')


def add_books(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        dates = request.POST.get("dates", "")

        title = request.POST.get("title", "")
        author = request.POST.get("author", "")
        classification = request.POST.get("classification", "")
        volume = request.POST.get("volume", "")
        publisher = request.POST.get("publisher", "")
        category = request.POST.get('category', "")
        yearPublication = request.POST.get("yearPublication", "")
        no_pages = request.POST.get("no_pages", "")
        purchased_from = request.POST.get("purchased_from", "")
        bill_no = request.POST.get("bill_no", "")
        bill_date = request.POST.get("bill_date", "")
        cost = request.POST.get("cost", "")
        edition = request.POST.get("edition", "")
        copies = request.POST.get("copies", "")
        ver = books.objects.all().last()

        request.session['copies'] = copies

        accession_no = ver.accession_number
        print(accession_no)

        asc_no = int(accession_no)
        asc_no += 1
        request.session['accession'] = asc_no
        print("acsno", asc_no)

        if dates == '':
            dates = datetime.date.today()
            print(dates)

        try:

            if category == 'select':
                messages.error(request, "select category")
                return redirect('/add_books')
            elif copies == '0':
                messages.error(request, "Number of Copies can't be 0")
                return redirect('/add_books')


            else:
                for j in range(0, int(copies)):
                    print("copies are", copies)

                    print("done1")
                    sig = books(accession_number=asc_no, dates=dates, title=title, author=author,
                                classification=classification, publisher=publisher, category=category,
                                yearPublication=yearPublication, no_pages=no_pages, purchased_from=purchased_from,
                                bill_no=bill_no, bill_date=bill_date, cost=cost, edition=edition, copies=copies,
                                volume=volume)
                    print('done2')

                    sig.save()
                    print("done3")
                    asc_no += 1
                    print("book added")
                    messages.error(request, "Book Added successfully")
                return redirect('/add_books')
        except:
            print("error")
            messages.error(request, "Enter valid data,Please try again")
            return redirect('/add_books')
    ver = books.objects.all().last()
    accession_no = ver.accession_number
    print(accession_no)

    return render(request, 'book_master.html', {'id': int(accession_no) + 1})


def qr_gen(request):
    if not request.user.is_authenticated:
        return redirect("/")
    try:
        list = []
        accession_no = request.session['accession']
        copies = int(request.session['copies'])
        for i in range(0, copies):
            hr = barcode.get_barcode_class('code128')
            qr = hr(str(accession_no), writer=ImageWriter())
            a = qr.save(r'C:\Users\OfficePC\PycharmProjects\mindlinks\library\static/' + str(accession_no))
            print(accession_no)
            qr_name = str(accession_no) + '.png'
            list.append(qr_name)
            print(list)

            accession_no += 1
        return render(request, 'barcode.html', {'list': list})
    except:
        messages.error(request, "There are some Errors!!Please try again")
        print("There are some Errors!!Please try again")
        return render(request, 'barcode.html')


def click_d(request):
    i = 0
    cap = cv2.VideoCapture(0)
    while i < 1:
        _, frame = cap.read()
        decoded = pyzbar.decode(frame)
        for obj in decoded:
            print(obj)
            a = obj.data.decode("ascii")
            b = str(a)
            print("the code is:", a)
            request.session['id1'] = b
            i = i + 1
            return render(request, 'Delete_Book.html', {'param': b})
        cv2.imshow("qrcode", frame)
        cv2.waitKey(100)
        cv2.destroyAllWindows()
    return redirect('/delete_books')


def get_d_b(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        accession_no = request.POST.get("accession_no", "")
        try:
            if accession_no == '':
                accession_no = request.session['id1']
            request.session['id1'] = accession_no

            ver = books.objects.get(accession_number=accession_no)
            if ver.deleted == "deleted":
                messages.error(request, "Already Deleted")
                return render(request, 'delete_b.html')
            else:

                return render(request, 'delete_b.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category,
                               "yearPublication": ver.yearPublication, "no_pages": ver.no_pages, "cost": ver.cost,
                               "edition": ver.edition, "volume": ver.volume})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            return render(request, 'delete_b.html')
    return render(request, 'Delete_Book.html')


def delete_books(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        accession_no = request.POST.get("accession_no", "")
        try:
            if accession_no == '':
                accession_no = request.session['id1']
            ver = books.objects.get(accession_number=accession_no)
            ver.deleted = "deleted"
            ver.save()
            messages.error(request, "Book deleted Successfully")
            print("delete done")
            return render(request, 'Delete_Book.html')
        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in delete")
            return render(request, 'Delete_Book.html')
    else:
        return render(request, 'Delete_Book.html', )


def click_w(request):
    i = 0
    cap = cv2.VideoCapture(0)
    while i < 1:
        _, frame = cap.read()
        decoded = pyzbar.decode(frame)
        for obj in decoded:
            print(obj)
            a = obj.data.decode("ascii")
            b = str(a)
            print("the code is:", a)
            request.session['id1'] = b
            i = i + 1
            return render(request, 'withdrawal.html', {'param': b})
        cv2.imshow("qrcode", frame)
        cv2.waitKey(100)
        cv2.destroyAllWindows()
    return redirect('/withdrawal_books')


def get_d_w(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        accession_no = request.POST.get("accession_no", "")
        dates = request.POST.get("dates", "")
        request.session['id2'] = dates
        try:
            if accession_no == '':
                accession_no = request.session['id1']
            request.session['id1'] = accession_no

            ver = books.objects.get(accession_number=accession_no)
            if ver.withdrawal_no != "":
                messages.error(request, "Already Write Off")
                return render(request, 'delete_w.html')
            else:

                return render(request, 'delete_w.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category,
                               "yearPublication": ver.yearPublication, "no_pages": ver.no_pages, "cost": ver.cost,
                               "edition": ver.edition, "volume": ver.volume})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            return render(request, 'delete_w.html')
    return render(request, 'withdrawal.html')


def withdrawal_books(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        accession_no = request.POST.get("accession_no", "")
        dates = request.session['id2']
        ver = books.objects.all().filter(~Q(withdrawal_no=''))
        wd_no = []
        for i in ver:
            wd_no.append(i.withdrawal_no)
        abc = max(wd_no)
        try:
            if accession_no == '':
                accession_no = request.session['id1']
            ver = books.objects.get(accession_number=accession_no)
            ver.withdrawal_no = int(abc) + 1
            ver.withdrawal_date = dates
            ver.save()
            messages.error(request, "Book withdrawal Successfully")

            return render(request, 'withdrawal.html')
        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in delete")
            return render(request, 'withdrawal.html')
    else:
        return render(request, 'withdrawal.html', )


def click_w_r(request):
    i = 0
    cap = cv2.VideoCapture(0)
    while i < 1:
        _, frame = cap.read()
        decoded = pyzbar.decode(frame)
        for obj in decoded:
            print(obj)
            a = obj.data.decode("ascii")
            b = str(a)
            print("the code is:", a)
            request.session['id1'] = b
            i = i + 1
            return render(request, 'write_in.html', {'param': b})
        cv2.imshow("qrcode", frame)
        cv2.waitKey(100)
        cv2.destroyAllWindows()
    return redirect('/write_in_books')


def get_d_w_r(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        accession_no = request.POST.get("accession_no", "")

        try:
            if accession_no == '':
                accession_no = request.session['id1']
            request.session['id1'] = accession_no

            ver = books.objects.get(accession_number=accession_no)
            if ver.withdrawal_no == "":
                messages.error(request, "Already Write in")
                return render(request, 'wrte_in_w.html')
            else:

                return render(request, 'wrte_in_w.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category,
                               "yearPublication": ver.yearPublication, "no_pages": ver.no_pages, "cost": ver.cost,
                               "edition": ver.edition, "volume": ver.volume})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            return render(request, 'wrte_in_w.html')
    return render(request, 'write_in.html')


def write_in_books(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        accession_no = request.POST.get("accession_no", "")

        try:
            if accession_no == '':
                accession_no = request.session['id1']
            ver = books.objects.get(accession_number=accession_no)
            ver.withdrawal_no = ''
            ver.withdrawal_date = None
            ver.save()
            messages.error(request, "Book Write In Successfully")

            return render(request, 'write_in.html')
        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in delete")
            return render(request, 'write_in.html')
    else:
        return render(request, 'write_in.html', )


def click_u(request):
    i = 0
    cap = cv2.VideoCapture(0)
    while i < 1:
        _, frame = cap.read()
        decoded = pyzbar.decode(frame)
        for obj in decoded:
            print(obj)
            a = obj.data.decode("ascii")
            b = str(a)
            print("the code is:", a)
            request.session['id1'] = b
            i = i + 1
            return render(request, 'notify4.html', {'param': b})
        cv2.imshow("qrcode", frame)
        cv2.waitKey(100)
        cv2.destroyAllWindows()

    return redirect('/get_u')


def get_u(request):
    if request.method == 'POST':
        accession_no = request.POST.get("accession_no", "")
        if accession_no == '':
            print("yse")
            accession_no = request.session['id1']

        request.session['id1'] = accession_no
        print("done")

        return redirect('/update_books')

    return render(request, 'notify4.html')


def update_books(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        title = request.POST.get('title', "")
        author = request.POST.get('author', "")
        classification = request.POST.get('classification', "")
        volume = request.POST.get('volume', "")
        publisher = request.POST.get('publisher', "")
        category = request.POST.get('category', "")
        yearpublication = request.POST.get('yearpublication', "")
        pages = request.POST.get('pages', "")
        cost = request.POST.get('cost', "")
        edition = request.POST.get('edition', "")
        bill_no = request.POST.get('bill_no', "")
        bill_date = request.POST.get('bill_date', "")
        dates = request.POST.get('dates', "")
        purchased_from = request.POST.get('purchased_from', "")
        accession_no = request.session['id1']

        try:

            if title != "":
                ver = books.objects.get(accession_number=accession_no)
                ver.title = title
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'book_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})

            elif author != "":
                ver = books.objects.get(accession_number=accession_no)
                ver.author = author
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'book_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})

            elif classification != "":
                ver = books.objects.get(accession_number=accession_no)
                ver.classification = classification
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'book_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})

            elif volume != "":
                ver = books.objects.get(accession_number=accession_no)
                ver.volume = volume
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'book_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})

            elif publisher != "":
                ver = books.objects.get(accession_number=accession_no)
                ver.publisher = publisher
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'book_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})

            elif category != "":
                ver = books.objects.get(accession_number=accession_no)
                ver.category = category
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'book_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})

            elif yearpublication != "":
                ver = books.objects.get(accession_number=accession_no)
                ver.yearPublication = yearpublication
                ver.save()
                print("done")
                messages.error(request, "Book updated Successfully")
                return render(request, 'book_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})

            elif pages != "":
                ver = books.objects.get(accession_number=accession_no)
                ver.no_pages = pages
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'book_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})
            elif cost != "":
                ver = books.objects.get(accession_number=accession_no)
                ver.cost = cost
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'book_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": bill_date, "dates": dates,
                               "purchased_from": purchased_from})

            elif edition != "":
                ver = books.objects.get(accession_number=accession_no)
                ver.edition = edition
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'book_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})
            elif bill_no != "":
                ver = books.objects.get(accession_number=accession_no)
                ver.bill_no = bill_no
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'book_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})

            elif bill_date != "":
                ver = books.objects.get(accession_number=accession_no)
                ver.bill_date = bill_date
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'book_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})

            elif dates != "":
                ver = books.objects.get(accession_number=accession_no)
                ver.dates = dates
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'book_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})

            elif purchased_from != "":
                ver = books.objects.get(accession_number=accession_no)
                ver.purchased_from = purchased_from
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'book_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})
            else:
                messages.error(request, "Enter valid data,Please try again ")
                return render(request, 'notify4.html')
        except:

            messages.error(request, "Enter valid data,Please try again")
            return render(request, 'notify4.html')
    else:
        try:
            accession_no = request.session['id1']
            ver = books.objects.get(accession_number=accession_no)
            return render(request, 'book_manage.html',
                          {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                           "classification": ver.classification, "publisher": ver.publisher,
                           "category": ver.category, "yearPublication": ver.yearPublication,
                           "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                           "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                           "dates": ver.dates,
                           "purchased_from": ver.purchased_from})
        except:

            return render(request, 'book_manage.html')


def add_stds(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        admission_no = request.POST.get("admission_no", "")
        dof_admission = request.POST.get("dof_admission", "")
        roll_no = request.POST.get("roll_no", "")
        std_name = request.POST.get("std_name", "")
        gender = request.POST.get("gender", "")
        dob = request.POST.get("dob", "")
        fname = request.POST.get('fname', "")
        mname = request.POST.get('mname', "")
        blood_group = request.POST.get('blood_group', "")
        expiry_date = request.POST.get('expiry_date', "")

        address1 = request.POST.get('address1', "")

        city = request.POST.get('city', "")

        state = request.POST.get('state', "")
        email = request.POST.get('email', "")
        contact = request.POST.get('contact', "")

        remarks = request.POST.get('remarks', "")

        ver = students.objects.all()
        for i in ver:
            if i.admission_no == admission_no:
                print("already exist")
                messages.success(request, "STUDENT already exist")
                return redirect('/add_stds')
            elif i.roll_no == roll_no:
                print("already exist")
                messages.success(request, "STUDENT already exist")
                return redirect('/add_stds')
        try:

            if blood_group == 'select':
                messages.success(request, "select category")
                return redirect('/add_stds')

            else:
                sig = students(admission_no=admission_no, dof_admission=dof_admission, roll_no=roll_no,
                               std_name=std_name, gender=gender, dob=dob, fname=fname, mname=mname,
                               blood_group=blood_group, expiry_date=expiry_date, city=city, state=state, email=email,
                               contact=contact, remarks=remarks, address1=address1)
                print('done2')
                sig.save()
                print("std added")
                messages.success(request, "STUDENT added succesfully")
                return redirect('/add_stds')
        except:
            print("error")
            messages.success(request, "Enter valid data,Please try again")
            return redirect('/add_stds')

    return render(request, 'student_master.html')


def update_stds(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        admission_no = request.POST.get("a_id", "")
        dof_admission = request.POST.get("doa", "")
        std_name = request.POST.get("name", "")
        gender = request.POST.get("gender", "")
        dob = request.POST.get("dob", "")
        fname = request.POST.get('father', "")
        mname = request.POST.get('mother', "")
        blood_group = request.POST.get('blood_group', "")
        expiry_date = request.POST.get('expiry_date', "")

        address1 = request.POST.get('address', "")

        city = request.POST.get('city', "")

        state = request.POST.get('state', "")

        email = request.POST.get('email', "")

        contact = request.POST.get('contact', "")

        remarks = request.POST.get('remarks', "")

        try:

            if dof_admission != "":
                ver2 = students.objects.get(roll_no=admission_no)
                ver2.dof_admission = dof_admission
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_student.html')
            elif std_name != "":
                ver2 = students.objects.get(roll_no=admission_no)
                ver2.std_name = std_name
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_student.html')
            elif gender != "":
                ver2 = students.objects.get(roll_no=admission_no)
                ver2.gender = gender
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_student.html')
            elif dob != "":
                ver2 = students.objects.get(roll_no=admission_no)
                ver2.dob = dob
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_student.html')
            elif fname != "":
                ver2 = students.objects.get(roll_no=admission_no)
                ver2.fname = fname
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_student.html')
            elif mname != "":
                ver2 = students.objects.get(roll_no=admission_no)
                ver2.mname = mname
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_student.html')
            elif blood_group != "":
                ver2 = students.objects.get(roll_no=admission_no)
                ver2.blood_group = blood_group
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_student.html')
            elif expiry_date != "":
                ver2 = students.objects.get(roll_no=admission_no)
                ver2.expiry_date = expiry_date
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_student.html')

            elif address1 != "":
                ver2 = students.objects.get(roll_no=admission_no)
                ver2.address1 = address1
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_student.html')

            elif city != "":
                ver2 = students.objects.get(roll_no=admission_no)
                ver2.city = city
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_student.html')

            elif state != "":
                ver2 = students.objects.get(roll_no=admission_no)
                ver2.state = state
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_student.html')
            elif email != "":
                ver2 = students.objects.get(roll_no=admission_no)
                ver2.email = email
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_student.html')
            elif contact != "":
                ver2 = students.objects.get(roll_no=admission_no)
                ver2.contact = contact
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_student.html')


            elif remarks != "":
                ver2 = students.objects.get(roll_no=admission_no)
                ver2.remarks = remarks
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_student.html')
            else:
                messages.error(request, "Enter valid data,Please try again ")
                return render(request, 'manage_student.html')
        except:

            messages.error(request, "Enter valid data,Please try again")
            return render(request, 'manage_student.html')
    else:
        try:
            return render(request, 'manage_student.html')
        except:
            return HttpResponse('404 error')


def get_d_s(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        emp_id = request.POST.get("a_id", "")
        request.session['id1'] = emp_id
        try:

            ver = students.objects.get(roll_no=emp_id)
            if ver.deleted == "deleted":
                messages.error(request, "Already Deleted")
                return render(request, 'delete_s.html')
            else:

                return render(request, 'delete_s.html',
                              {'admission_no': ver.admission_no, "dof_admission": ver.dof_admission,
                               "roll_no": ver.roll_no, "std_name": ver.std_name,
                               "gender": ver.gender, "dob": ver.dob, "fname": ver.fname,
                               "mname": ver.mname, "email": ver.email, "contact": ver.contact,
                               "address1": ver.address1, "city": ver.city, 'state': ver.state})


        except:
            messages.error(request, "There are some Errors!!Please try again")
            return render(request, 'delete_s.html')
    return render(request, 'delete_stds.html')


def delete_stds(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        try:
            admission_no = request.session['id1']
            ver2 = students.objects.get(roll_no=admission_no)
            ver2.deleted = "deleted"
            ver2.save()
            messages.error(request, "Deleted Successfully")
            print("delete done")
            return render(request, 'delete_stds.html')
        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in delete")
            return render(request, 'delete_stds.html')
    else:

        try:
            return render(request, 'delete_stds.html')
        except:
            return HttpResponse('404 error')


def add_employ(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        emp_id = request.POST.get("emp_id", "")
        dof_join = request.POST.get("dof_join", "")
        emp_name = request.POST.get("emp_name", "")
        gender = request.POST.get("gender", "")
        dob = request.POST.get("dob", "")
        fname = request.POST.get('fname', "")
        spouse_name = request.POST.get('spouse_name', "")
        email = request.POST.get('email', "")
        address1 = request.POST.get('address1', "")

        contact = request.POST.get('contact', "")

        city = request.POST.get('city', "")

        state = request.POST.get('state', "")
        has_left = request.POST.get('has_left', "")
        incharge = request.POST.get('incharge', "")

        try:
            ver = employees.objects.all()
            for i in ver:
                if i.emp_id == emp_id:
                    print("already exist")
                    messages.error(request, "Employee already exist")
                    return redirect('/add_employ')
            else:
                sig = employees(emp_id=emp_id, dof_join=dof_join, emp_name=emp_name, gender=gender, dob=dob,
                                fname=fname, spouse_name=spouse_name, city=city, state=state, email=email,
                                contact=contact, has_left=has_left, incharge=incharge, address1=address1)
                print('done2')
                sig.save()
                print("employ added")
                messages.error(request, "Employee added succesfully")
                return redirect('/add_employ')
        except:
            print("error")
            messages.error(request, "Enter valid data,Please try again")
            return redirect('/add_employ')

    return render(request, 'employee_master.html')


def update_employ(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        emp_id = request.POST.get("e_id", "")
        dof_join = request.POST.get("doj", "")
        emp_name = request.POST.get("name", "")
        gender = request.POST.get("gender", "")
        dob = request.POST.get("dob", "")
        fname = request.POST.get('father', "")
        spouse_name = request.POST.get('spouse', "")
        email = request.POST.get('email', "")
        address1 = request.POST.get('address', "")

        contact = request.POST.get('contact', "")

        city = request.POST.get('city', "")

        state = request.POST.get('state', "")
        has_left = request.POST.get('has_left', "")
        incharge = request.POST.get('incharge', "")
        try:

            if dof_join != "":
                ver2 = employees.objects.get(emp_id=emp_id)
                ver2.dof_join = dof_join
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_employee.html')
            elif emp_name != "":
                ver2 = employees.objects.get(emp_id=emp_id)
                ver2.emp_name = emp_name
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_employee.html')
            elif gender != "":
                ver2 = employees.objects.get(emp_id=emp_id)
                ver2.gender = gender
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_employee.html')
            elif dob != "":
                ver2 = employees.objects.get(emp_id=emp_id)
                ver2.dob = dob
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_employee.html')
            elif fname != "":
                ver2 = employees.objects.get(emp_id=emp_id)
                ver2.fname = fname
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_employee.html')
            elif spouse_name != "":
                ver2 = employees.objects.get(emp_id=emp_id)
                ver2.spouse_name = spouse_name
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_employee.html')

            elif address1 != "":
                ver2 = employees.objects.get(emp_id=emp_id)
                ver2.address1 = address1
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_employee.html')

            elif city != "":
                ver2 = employees.objects.get(emp_id=emp_id)
                ver2.city = city
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_employee.html')

            elif state != "":
                ver2 = employees.objects.get(emp_id=emp_id)
                ver2.state = state
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_employee.html')
            elif email != "":
                ver2 = employees.objects.get(emp_id=emp_id)
                ver2.email = email
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_employee.html')
            elif contact != "":
                ver2 = employees.objects.get(emp_id=emp_id)
                ver2.contact = contact
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_employee.html')

            elif has_left != "":
                ver2 = employees.objects.get(emp_id=emp_id)
                ver2.has_left = has_left
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_employee.html')
            elif incharge != "":
                ver2 = employees.objects.get(emp_id=emp_id)
                ver2.incharge = incharge
                ver2.save()
                messages.error(request, "Updated Successfully")
                return render(request, 'manage_employee.html')

            else:
                messages.error(request, "Enter valid data,Please try again ")
                return render(request, 'manage_employee.html')
        except:

            messages.error(request, "Enter valid data,Please try again")
            return render(request, 'manage_employee.html')
    else:
        try:
            return render(request, 'manage_employee.html')
        except:
            return HttpResponse('404 error')


def get_d_e(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        emp_id = request.POST.get("a_id", "")
        request.session['id1'] = emp_id
        try:

            ver = employees.objects.get(emp_id=emp_id)
            if ver.deleted == "deleted":
                messages.error(request, "Already Deleted")
                return render(request, 'delete_e.html')
            else:

                return render(request, 'delete_e.html',
                              {'emp_id': ver.emp_id, "dof_join": ver.dof_join, "emp_name": ver.emp_name,
                               "gender": ver.gender, "dob": ver.dob, "fname": ver.fname,
                               "spouse_name": ver.spouse_name, "email": ver.email, "contact": ver.contact,
                               "address1": ver.address1, "city": ver.city, 'state': ver.state})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            return render(request, 'delete_e.html')
    return render(request, 'delete_employ.html')


def delete_employ(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        try:
            emp_id = request.session['id1']
            ver2 = employees.objects.get(emp_id=emp_id)
            ver2.deleted = "deleted"
            ver2.save()
            messages.error(request, "Deleted Successfully")
            print("delete done")
            return render(request, 'delete_employ.html')
        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in delete")
            return render(request, 'delete_employ.html')
    else:

        try:
            return render(request, 'delete_employ.html')
        except:
            return HttpResponse('404 error')


def student_list(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        date1 = request.POST.get("date", "")
        month = request.POST.get("month", "")
        title = request.POST.get("title", "")
        year = request.POST.get("year", "")
        roll_no = request.POST.get("roll_no", "")
        try:
            if date1 != '' and month != '' and year != '' and title != '':
                ver3 = students.objects.all().filter(std_name__icontains=title).filter(dof_admission__year=year,
                                                                                       dof_admission__month=month,
                                                                                       dof_admission__day=date1).order_by(
                    'dof_admission')
                return render(request, 'r_student.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title != '':
                ver3 = students.objects.all().filter(dof_admission__year=year, dof_admission__month=month).filter(
                    std_name__icontains=title).order_by('dof_admission')
                return render(request, 'r_student.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = students.objects.all().filter(dof_admission__year=year).filter(
                    std_name__icontains=title).order_by('dof_admission')
                return render(request, 'r_student.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title != '':
                ver3 = students.objects.all().filter(std_name__icontains=title).order_by('dof_admission')
                return render(request, 'r_student.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year != '' and title == '':
                ver3 = students.objects.all().filter(dof_admission__year=year, dof_admission__month=month,
                                                     dof_admission__day=date1).order_by('dof_admission')
                return render(request, 'r_student.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title == '':
                ver3 = students.objects.all().filter(dof_admission__month=month, dof_admission__day=date1).order_by(
                    'dof_admission')
                return render(request, 'r_student.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title == '':
                ver3 = students.objects.all().filter(dof_admission__day=date1).order_by('dof_admission')
                return render(request, 'r_student.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title != '':
                ver3 = students.objects.all().filter(std_name__icontains=title).filter(dof_admission__year=year,
                                                                                       dof_admission__day=date1).order_by(
                    'dof_admission')
                return render(request, 'r_student.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title != '':
                ver3 = students.objects.all().filter(std_name__icontains=title).filter(
                    dof_admission__day=date1).order_by('dof_admission')
                return render(request, 'r_student.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title != '':
                ver3 = students.objects.all().filter(std_name__icontains=title).filter(dof_admission__month=month,
                                                                                       dof_admission__day=date1).order_by(
                    'dof_admission')
                return render(request, 'r_student.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title != '':
                ver3 = students.objects.all().filter(std_name__icontains=title).filter(
                    dof_admission__month=month).order_by('dof_admission')
                return render(request, 'r_student.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = students.objects.all().filter(std_name__icontains=title).filter(
                    dof_admission__year=year).order_by('dof_admission')
                return render(request, 'r_student.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title == '':
                ver3 = students.objects.all().filter(dof_admission__year=year).order_by('dof_admission')
                return render(request, 'r_student.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title == '':
                ver3 = students.objects.all().filter(dof_admission__month=month).order_by('dof_admission')
                return render(request, 'r_student.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title == '':
                ver3 = students.objects.all().filter(dof_admission__year=year, dof_admission__day=date1).order_by(
                    'dof_admission')
                return render(request, 'r_student.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title == '':
                ver3 = students.objects.all().filter(dof_admission__year=year, dof_admission__month=month).order_by(
                    'dof_admission')
                return render(request, 'r_student.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '' and roll_no!='':
                ver3 = students.objects.all().order_by('dof_admission').filter(roll_no=roll_no)
                return render(request, 'r_student.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '':
                ver3 = students.objects.all().order_by('dof_admission')
                return render(request, 'r_student.html', {'query_results': ver3})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in list")
            return render(request, 'list4.html')
    else:
        return render(request, 'list4.html')


def employee_list(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        date1 = request.POST.get("date", "")
        month = request.POST.get("month", "")
        title = request.POST.get("title", "")
        year = request.POST.get("year", "")
        emp_id = request.POST.get("emp_id", "")
        try:
            if date1 != '' and month != '' and year != '' and title != '':
                ver3 = employees.objects.all().filter(emp_name__icontains=title).filter(dof_join__year=year,
                                                                                        dof_join__month=month,
                                                                                        dof_join__day=date1).order_by(
                    'dof_join')
                return render(request, 'r_employee.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title != '':
                ver3 = employees.objects.all().filter(dof_join__year=year, dof_join__month=month).filter(
                    emp_name__icontains=title).order_by('dof_join')
                return render(request, 'r_employee.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = employees.objects.all().filter(dof_join__year=year).filter(emp_name__icontains=title).order_by(
                    'dof_join')
                return render(request, 'r_employee.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title != '':
                ver3 = employees.objects.all().filter(emp_name__icontains=title).order_by('dof_join')
                return render(request, 'r_employee.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year != '' and title == '':
                ver3 = employees.objects.all().filter(dof_join__year=year, dof_join__month=month,
                                                      dof_join__day=date1).order_by('dof_join')
                return render(request, 'r_employee.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title == '':
                ver3 = employees.objects.all().filter(dof_join__month=month, dof_join__day=date1).order_by('dof_join')
                return render(request, 'r_employee.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title == '':
                ver3 = employees.objects.all().filter(dof_join__day=date1).order_by('dof_join')
                return render(request, 'r_employee.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title != '':
                ver3 = employees.objects.all().filter(emp_name__icontains=title).filter(dof_join__year=year,
                                                                                        dof_join__day=date1).order_by(
                    'dof_join')
                return render(request, 'r_employee.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title != '':
                ver3 = employees.objects.all().filter(emp_name__icontains=title).filter(dof_join__day=date1).order_by(
                    'dof_join')
                return render(request, 'r_employee.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title != '':
                ver3 = employees.objects.all().filter(emp_name__icontains=title).filter(dof_join__month=month,
                                                                                        dof_join__day=date1).order_by(
                    'dof_join')
                return render(request, 'r_employee.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title != '':
                ver3 = employees.objects.all().filter(emp_name__icontains=title).filter(dof_join__month=month).order_by(
                    'dof_join')
                return render(request, 'r_employee.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = employees.objects.all().filter(emp_name__icontains=title).filter(dof_join__year=year).order_by(
                    'dof_join')
                return render(request, 'r_employee.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title == '':
                ver3 = employees.objects.all().filter(dof_join__year=year).order_by('dof_join')
                return render(request, 'r_employee.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title == '':
                ver3 = employees.objects.all().filter(dof_join__month=month).order_by('dof_join')
                return render(request, 'r_employee.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title == '':
                ver3 = employees.objects.all().filter(dof_join__year=year, dof_join__day=date1).order_by('dof_join')
                return render(request, 'r_employee.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title == '':
                ver3 = employees.objects.all().filter(dof_join__year=year, dof_join__month=month).order_by('dof_join')
                return render(request, 'r_employee.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '' and emp_id!='':
                ver3 = employees.objects.all().order_by('dof_join').filter(emp_id=emp_id)
                return render(request, 'r_employee.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '':
                ver3 = employees.objects.all().order_by('dof_join')
                return render(request, 'r_employee.html', {'query_results': ver3})
        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in list")
            return render(request, 'list5.html')
    else:
        return render(request, 'list5.html')


def barcode_gen(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        try:
            list = []
            ab = request.POST.get("start", "")
            accession_no = int(ab)
            copies = request.POST.get("end", "")
            n = int(copies) - int(ab)
            print(n)
            for i in range(0, n + 1):
                hr = barcode.get_barcode_class('code128')
                qr = hr(str(accession_no), writer=ImageWriter())
                a = qr.save(r'C:\Users\OfficePC\PycharmProjects\mindlinks\library\static/' + str(accession_no))
                print(accession_no)
                qr_name = str(accession_no) + '.png'

                list.append(qr_name)
                print(list)

                accession_no += 1

            return render(request, 'barcode.html', {'list': list})
        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in barcode")
            return render(request, 'Barcode_genrator.html')
    return render(request, 'Barcode_genrator.html')


def click_i_s(request):
    i = 0
    cap = cv2.VideoCapture(0)
    while i < 1:
        _, frame = cap.read()
        decoded = pyzbar.decode(frame)
        for obj in decoded:
            print(obj)
            a = obj.data.decode("ascii")
            b = str(a)
            print("the code is:", a)
            request.session['id1'] = b
            i = i + 1
            return render(request, 'notify.html', {'param': b})
        cv2.imshow("qrcode", frame)
        cv2.waitKey(100)
        cv2.destroyAllWindows()
    return redirect('/get_i_s')


def get_i_s(request):
    if request.method == 'POST':
        emp_id = request.POST.get("a_id", "")
        request.session['id2'] = emp_id
        accession_no = request.POST.get("accession_no", "")
        if accession_no == '':
            print("yse")
            accession_no = request.session['id1']

        request.session['id1'] = accession_no
        print("done")

        return redirect('/issue_books_s')

    return render(request, 'notify.html')


def issue_books_s(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':

        accession_id = request.session['id1']

        student_id = request.session['id2']
        issue = request.POST.get("issue_date", "")

        issue_date = datetime.datetime.strptime(issue, '%Y-%m-%d')

        due_day = request.POST.get("due_days", "")

        due_date = issue_date + datetime.timedelta(days=int(due_day))

        fine = 0
        ver1 = books.objects.get(accession_number=accession_id)
        ver2 = students.objects.get(roll_no=student_id)
        try:

            sig = manage_books(accession_id=accession_id, title=ver1.title, student_id=student_id,
                               std_name=ver2.std_name, issue_date=issue_date, due_date=due_date, fine=fine)
            sig.save()

            ver1 = students.objects.get(admission_no=student_id)
            no_books = ver1.no_books
            ver1.no_books = no_books + 1
            ver1.save()

            ver2 = books.objects.get(accession_number=accession_id)
            copy1 = ver2.copies
            ver2.copies = copy1 - 1
            ver2.save()
            messages.info(request, "Book Issued Successfully")
            return render(request, 'notify.html')
        except:

            return render(request, 'notify.html')
    else:
        try:
            accession_id = request.session['id1']

            ver3 = manage_books.objects.all().order_by('issue_date').reverse()

            for i in ver3:
                if i.accession_id == accession_id:
                    if i.issued == 'yes':
                        messages.info(request, "Already Issued Book")
                        return render(request, 'issue_book_s.html')
            print("pass4")
            ver1 = books.objects.get(accession_number=accession_id)

            if ver1.copies == 0:
                messages.info(request, "Book is not Available")
                return render(request, 'issue_book_s.html')
            elif ver1.withdrawal_no != '':
                messages.info(request, "Book is not Available")
                return render(request, 'issue_book_s.html')

            student_id = request.session['id2']

            ver2 = students.objects.get(roll_no=student_id)
            if ver2.deleted == 'deleted':
                messages.info(request, "Can't Issue Book")
                return render(request, 'issue_book_s.html')

            param = {"id": student_id, "name": ver2.std_name, "fname": ver2.fname, "gender": ver2.gender,
                     "contact_no": ver2.contact, "left": "No", "a_id": accession_id, "title": ver1.title,
                     "yop": ver1.yearPublication, "nop": ver1.no_pages, "cob": ver1.cost, "edition": ver1.edition,
                     "no_book": ver2.no_books}
            print(param)

            return render(request, 'issue_book_s.html', param)
        except:
            messages.info(request, "No such record")
            return render(request, 'issue_book_s.html')


def click_i_e(request):
    i = 0
    cap = cv2.VideoCapture(0)
    while i < 1:
        _, frame = cap.read()
        decoded = pyzbar.decode(frame)
        for obj in decoded:
            print(obj)
            a = obj.data.decode("ascii")
            b = str(a)
            print("the code is:", a)
            request.session['id1'] = b
            i = i + 1
            return render(request, 'notify1.html', {'param': b})
        cv2.imshow("qrcode", frame)
        cv2.waitKey(100)
        cv2.destroyAllWindows()
    return redirect('/get_i_e')


def get_i_e(request):
    if request.method == 'POST':
        emp_id = request.POST.get("a_id", "")
        request.session['id2'] = emp_id
        accession_no = request.POST.get("accession_no", "")
        if accession_no == '':
            print("yse")
            accession_no = request.session['id1']

        request.session['id1'] = accession_no
        print("done")

        return redirect('/issue_books_e')

    return render(request, 'notify1.html')


def issue_books_e(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':

        accession_id = request.session['id1']

        emp_id = request.session['id2']
        issue = request.POST.get("issue_date", "")

        issue_date = datetime.datetime.strptime(issue, '%Y-%m-%d')

        due_day = request.POST.get("due_days", "")

        due_date = issue_date + datetime.timedelta(days=int(due_day))

        fine = 0
        ver1 = books.objects.get(accession_number=accession_id)
        ver2 = employees.objects.get(emp_id=emp_id)
        try:

            sig = manage_books(accession_id=accession_id, title=ver1.title, emp_id=emp_id, emp_name=ver2.emp_name,
                               issue_date=issue_date, due_date=due_date, fine=fine)
            sig.save()

            ver1 = employees.objects.get(emp_id=emp_id)
            no_books = ver1.no_books
            ver1.no_books = no_books + 1
            ver1.save()

            ver2 = books.objects.get(accession_number=accession_id)
            copy1 = ver2.copies
            ver2.copies = copy1 - 1
            ver2.save()
            messages.info(request, "Book Issued Successfully")
            return render(request, 'notify1.html')
        except:
            messages.info(request, "Enter valid data,Please try again")
            return render(request, 'notify1.html')
    else:
        try:

            accession_id = request.session['id1']
            ver3 = manage_books.objects.all().order_by('issue_date').reverse()

            for i in ver3:
                if i.accession_id == accession_id:
                    if i.issued == 'yes':
                        messages.info(request, "Already Issued Book")
                        return render(request, 'issue_book_e.html')
            print("pass4")

            ver1 = books.objects.get(accession_number=accession_id)
            print(ver1.copies, type(ver1.copies))
            if ver1.copies == 0:
                messages.info(request, "Book is not Available")
                return render(request, 'issue_book_e.html')
            elif ver1.withdrawal_no != '':
                messages.info(request, "Book is not Available")
                return render(request, 'issue_book_e.html')
            emp_id = request.session['id2']

            ver2 = employees.objects.get(emp_id=emp_id)
            if ver2.deleted == 'deleted':
                messages.info(request, "Can't Issue Book")
                return render(request, 'issue_book_e.html')

            param = {"id": emp_id, "name": ver2.emp_name, "fname": ver2.fname, "gender": ver2.gender,
                     "contact_no": ver2.contact, "left": "No", "a_id": accession_id, "title": ver1.title,
                     "yop": ver1.yearPublication, "nop": ver1.no_pages, "cob": ver1.cost, "edition": ver1.edition,
                     "no_book": ver2.no_books}
            print(param)
            return render(request, 'issue_book_e.html', param)

        except:
            messages.info(request, "No such record")
            return render(request, 'issue_book_e.html')


def click_r_s(request):
    i = 0
    cap = cv2.VideoCapture(0)
    while i < 1:
        _, frame = cap.read()
        decoded = pyzbar.decode(frame)
        for obj in decoded:
            print(obj)
            a = obj.data.decode("ascii")
            b = str(a)
            print("the code is:", a)
            request.session['id1'] = b
            i = i + 1
            return render(request, 'notify2.html', {'param': b})
        cv2.imshow("qrcode", frame)
        cv2.waitKey(100)
        cv2.destroyAllWindows()
    return redirect('/get_r_s')


def get_r_s(request):
    if request.method == 'POST':
        accession_no = request.POST.get("a_id", "")
        if accession_no == '':
            print("yse")
            accession_no = request.session['id1']

        request.session['id1'] = accession_no
        print("done")

        return redirect('/return_books_s')

    return render(request, 'notify2.html')


def return_books_s(request):
    if request.method == 'POST':
        return_dates = request.POST.get("return_date", "")
        print(return_dates)
        return_date = datetime.datetime.strptime(return_dates, '%Y-%m-%d').date()


        try:
            accession_id = request.session['id1']

                # emp_id = request.session['id2']

            ver3 = manage_books.objects.all().order_by('issue_date').reverse()
            for i in ver3:
                if i.accession_id == accession_id:
                    i.return_date = return_date
                    i.returned = "yes"
                    i.issued = "no"
                    i.fine = 0

                    i.save()
                    ver1 = students.objects.get(roll_no=i.student_id)
                    no_books = ver1.no_books
                    ver1.no_books = no_books - 1
                    ver1.save()
                    ver2 = books.objects.get(accession_number=accession_id)
                    copy1 = ver2.copies
                    ver2.copies = copy1 + 1
                    ver2.save()
            messages.info(request, "Book Returned Successfully")
            return render(request, 'notify2.html')
        except:
            messages.info(request, "Book Returned Successfully")
            return render(request, 'notify2.html')

    else:
        try:
            accession_id = request.session['id1']
            print(accession_id)
            # emp_id = request.session['id2']

            ver3 = manage_books.objects.all().order_by('issue_date').reverse()

            for i in ver3:
                if i.accession_id == accession_id:
                    print(i.returned)
                    if i.returned == 'yes' and i.issued == 'no':
                        messages.info(request, "Already Returned Book")
                        return render(request, 'return_book_s.html')
                    ver2 = students.objects.get(roll_no=i.student_id)
                    ver1 = books.objects.get(accession_number=accession_id)
                    param = {"id": ver2.roll_no, "name": ver2.std_name, "fname": ver2.fname, "gender": ver2.gender,
                             "contact_no": ver2.contact, "left": "No", "a_id": accession_id, "title": ver1.title,
                             "yop": ver1.yearPublication, "nop": ver1.no_pages, "cob": ver1.cost,
                             "edition": ver1.edition, "fine": i.fine, "i_date": i.issue_date, "r_date": i.due_date,
                             "no_book": ver2.no_books}
                    print(param)
                    return render(request, 'return_book_s.html', param)
            print("d8")
            messages.info(request, "No such record")
            return render(request, 'return_book_s.html')

        except:
            messages.info(request, "No such record")
            return render(request, 'return_book_s.html')


def click_r_e(request):
    i = 0
    cap = cv2.VideoCapture(0)
    while i < 1:
        _, frame = cap.read()
        decoded = pyzbar.decode(frame)
        for obj in decoded:
            print(obj)
            a = obj.data.decode("ascii")
            b = str(a)
            print("the code is:", a)
            request.session['id1'] = b
            i = i + 1
            return render(request, 'notify3.html', {'param': b})
        cv2.imshow("qrcode", frame)
        cv2.waitKey(100)
        cv2.destroyAllWindows()
    return redirect('/get_r_e')


def get_r_e(request):
    if request.method == 'POST':
        accession_no = request.POST.get("a_id", "")
        if accession_no == '':
            print("yse")
            accession_no = request.session['id1']

        request.session['id1'] = accession_no
        print("done")

        return redirect('/return_books_e')

    return render(request, 'notify3.html')


def return_books_e(request):
    if request.method == 'POST':
        return_dates = request.POST.get("return_date", "")
        print(return_dates)
        return_date = datetime.datetime.strptime(return_dates, '%Y-%m-%d').date()

        try:
            accession_id = request.session['id1']

            # emp_id = request.session['id2']

            ver3 = manage_books.objects.all().order_by('issue_date').reverse()
            for i in ver3:
                if i.accession_id == accession_id:
                    i.return_date = return_date
                    i.returned = "yes"
                    i.issued = "no"
                    i.fine = 0
                    i.save()
                    ver1 = employees.objects.get(emp_id=i.emp_id)
                    no_books = ver1.no_books
                    print(no_books - 1)
                    ver1.no_books = no_books - 1
                    ver1.save()
                    ver2 = books.objects.get(accession_number=accession_id)
                    copy1 = ver2.copies
                    ver2.copies = copy1 + 1
                    ver2.save()
            messages.info(request, "Book Returned Successfully")
            return render(request, 'notify3.html')
        except:
            messages.info(request, "Book Returned Successfully")
            return render(request, 'notify3.html')

    else:
        try:
            accession_id = request.session['id1']
            print(accession_id)
            # emp_id = request.session['id2']

            ver3 = manage_books.objects.all().order_by('issue_date').reverse()
            print(ver3)
            for i in ver3:
                if i.accession_id == accession_id:
                    print(i.returned)
                    if i.returned == 'yes':
                        messages.info(request, "Already Returned Book")
                        return render(request, 'return_book_e.html')
                    ver2 = employees.objects.get(emp_id=i.emp_id)
                    ver1 = books.objects.get(accession_number=accession_id)
                    param = {"id": ver2.emp_id, "name": ver2.emp_name, "fname": ver2.fname, "gender": ver2.gender,
                             "contact_no": ver2.contact, "left": "No", "a_id": accession_id, "title": ver1.title,
                             "yop": ver1.yearPublication, "nop": ver1.no_pages, "cob": ver1.cost,
                             "edition": ver1.edition, "fine": i.fine, "i_date": i.issue_date, "r_date": i.due_date,
                             "no_book": ver2.no_books}
                    print(param)
                    return render(request, 'return_book_e.html', param)
            print("d8")
            messages.info(request, "No such record")
            return render(request, 'return_book_e.html')

        except:
            messages.info(request, "No such record")
            return render(request, 'return_book_e.html')


def newspapers(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        name1 = request.POST.get("name1", "")
        date_of_receipt = request.POST.get("date_of_receipt", "")

        price = request.POST.get("price", "")

        language = request.POST.get("language", "")

        try:
            sig = newspaper(date_of_receipt=date_of_receipt, title=name1, price=price, language=language)
            print('done2')
            sig.save()

            messages.info(request, "Newspaper added Successfully")

            return render(request, 'newspaper.html')
        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in delete")
            return render(request, 'newspaper.html')
    else:
        return render(request, 'newspaper.html', )


def journal(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        name1 = request.POST.get("name1", "")
        date_of_receipt = request.POST.get("date_of_receipt", "")

        price = request.POST.get("price", "")

        language = request.POST.get("language", "")
        publisher = request.POST.get('publisher', "")
        supplier = request.POST.get('supplier', "")
        s_email = request.POST.get("s_email", "")
        s_contact = request.POST.get("s_contact", "")
        type = request.POST.get('type', "")
        frequency = request.POST.get('frequency', "")
        volume = request.POST.get("volume", "")
        no1 = request.POST.get("no1", "")
        year = request.POST.get("year", "")
        issn_no = request.POST.get("issn_no", "")

        try:
            sig = newspaper(date_of_receipt=date_of_receipt, title=name1, price=price, language=language,
                            publisher=publisher, supplier=supplier, s_email=s_email, s_contact=s_contact, type=type,
                            frequency=frequency, volume=volume, no1=no1, year=year, issn_no=issn_no)
            print('done2')
            sig.save()

            messages.success(request, "Journal added Successfully")

            return render(request, 'journals.html')
        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in delete")
            return render(request, 'journals.html')
    else:
        return render(request, 'journals.html', )


def accession_register(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        start_date = request.POST.get("dates", "")
        end_date = request.POST.get("dates1", "")
        title = request.POST.get("title", "")
        category = request.POST.get("category", "")
        deleted = request.POST.get("deleted", "")
        title_wise = request.POST.get("title_wise", "")
        category_wise = request.POST.get("category_wise", "")
        withdrawal = request.POST.get("withdrawal", "")


        try:
            if title_wise != '' and start_date == '' and end_date == '' and deleted == '' and withdrawal == '' and category == '' and title == '':

                obj = books.objects.all().values('title', 'author', 'publisher').annotate(dcount=Count('title'))
                print(obj)
                return render(request, 'report1.html', {'query_results': obj})
            elif category_wise != '' and start_date == '' and end_date == '' and deleted == '' and withdrawal == '' and category == '' and title == '':
                obj = books.objects.all().values('category').annotate(dcount=Count('category'))
                print(obj)
                return render(request, 'report2.html', {'query_results': obj})


            elif start_date != '' and end_date != '' and deleted != '' and withdrawal != '' and category != '' and title != '':
                print("done1")
                obj = books.objects.all().filter(dates__range=(start_date, end_date)).filter(
                    title__icontains=title).filter(category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and deleted != '' and withdrawal != '' and category != '' and title == '':
                print('done2')
                obj = books.objects.all().filter(dates__range=(start_date, end_date)).filter(withdrawal_no='').filter(
                    category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and deleted != '' and withdrawal != '' and category == '' and title != '':
                print('done3')
                obj = books.objects.all().filter(dates__range=(start_date, end_date)).filter(withdrawal_no='').filter(
                    title__icontains=title)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and deleted != '' and withdrawal != '' and category == '' and title == '':
                print('done4')
                obj = books.objects.all().filter(dates__range=(start_date, end_date)).filter(withdrawal_no='')
                return render(request, 'report.html', {'query_results': obj})


            elif start_date != '' and end_date != '' and deleted != '' and withdrawal == '' and category != '' and title != '':
                print('done5')
                obj = books.objects.all().filter(dates__range=(start_date, end_date)).filter(withdrawal_no='').filter(
                    title__icontains=title).filter(category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and deleted != '' and withdrawal == '' and category != '' and title == '':
                print('done6')
                obj = books.objects.all().filter(dates__range=(start_date, end_date)).filter(withdrawal_no='').filter(
                    category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and deleted != '' and withdrawal == '' and category == '' and title != '':
                print('done7')
                obj = books.objects.all().filter(dates__range=(start_date, end_date)).filter(withdrawal_no='').filter(
                    title__icontains=title)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and deleted != '' and withdrawal == '' and category == '' and title == '':
                print('done8')
                obj = books.objects.all().filter(dates__range=(start_date, end_date)).filter(withdrawal_no='')
                return render(request, 'report.html', {'query_results': obj})


            elif start_date != '' and end_date != '' and withdrawal != '' and deleted == '' and category != '' and title != '':
                print('done9')
                obj = books.objects.all().filter(dates__range=(start_date, end_date)).filter(deleted='').filter(
                    title__icontains=title).filter(category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and withdrawal != '' and deleted == '' and category != '' and title == '':
                print('done10')
                obj = books.objects.all().filter(dates__range=(start_date, end_date)).filter(deleted='').filter(
                    category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and withdrawal != '' and deleted == '' and category == '' and title != '':
                print('done11')
                obj = books.objects.all().filter(dates__range=(start_date, end_date)).filter(deleted='').filter(
                    title__icontains=title)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and withdrawal != '' and deleted == '' and category == '' and title == '':
                print('done12')
                obj = books.objects.all().filter(dates__range=(start_date, end_date)).filter(deleted='')
                return render(request, 'report.html', {'query_results': obj})


            elif start_date == '' and end_date == '' and withdrawal != '' and deleted == '' and category != '' and title != '':
                print("done13")
                obj = books.objects.all().filter(deleted='').filter(title__icontains=title).filter(
                    category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date == '' and end_date == '' and withdrawal != '' and deleted == '' and category != '' and title == '':
                print("done14")
                obj = books.objects.all().filter(deleted='').filter(category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date == '' and end_date == '' and withdrawal != '' and deleted == '' and category == '' and title != '':
                print("done15")
                obj = books.objects.all().filter(deleted='').filter(title__icontains=title)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date == '' and end_date == '' and withdrawal != '' and deleted == '' and category == '' and title == '':
                print("done16")
                obj = books.objects.all().filter(deleted='')
                return render(request, 'report.html', {'query_results': obj})


            elif start_date == '' and end_date == '' and deleted != '' and withdrawal == '' and category != '' and title != '':
                print("done17")
                obj = books.objects.all().filter(withdrawal_no='').filter(title__icontains=title).filter(
                    category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date == '' and end_date == '' and deleted != '' and withdrawal == '' and category != '' and title == '':
                print("done18")
                obj = books.objects.all().filter(withdrawal_no='').filter(category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date == '' and end_date == '' and deleted != '' and withdrawal == '' and category == '' and title != '':
                print("done19")
                obj = books.objects.all().filter(withdrawal_no='').filter(title__icontains=title)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date == '' and end_date == '' and deleted != '' and withdrawal == '' and category == '' and title == '':
                print("done20")
                obj = books.objects.all().filter(withdrawal_no='')
                return render(request, 'report.html', {'query_results': obj})



            elif start_date == '' and end_date == '' and withdrawal != '' and deleted != '' and category != '' and title != '':
                print('done21')
                obj = books.objects.all().filter(title__icontains=title).filter(category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date == '' and end_date == '' and withdrawal != '' and deleted != '' and category != '' and title == '':
                print('d22')
                obj = books.objects.all().filter(category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date == '' and end_date == '' and withdrawal != '' and deleted != '' and category == '' and title != '':
                print('dw23')
                obj = books.objects.all().filter(title__icontains=title)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date == '' and end_date == '' and withdrawal != '' and deleted != '' and category == '' and title == '':
                print('dw24')
                obj = books.objects.all()
                return render(request, 'report.html', {'query_results': obj})



            elif start_date != '' and end_date != '' and deleted == '' and withdrawal == '' and category != '' and title != '':
                print("done25")
                obj = books.objects.all().filter(dates__range=(start_date, end_date)).filter(withdrawal_no='').filter(
                    deleted='').filter(title__icontains=title).filter(category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and deleted == '' and withdrawal == '' and category != '' and title == '':
                print("done26")
                obj = books.objects.all().filter(dates__range=(start_date, end_date)).filter(withdrawal_no='').filter(
                    deleted='').filter(category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and deleted == '' and withdrawal == '' and category == '' and title != '':
                print("done27")
                obj = books.objects.all().filter(dates__range=(start_date, end_date)).filter(withdrawal_no='').filter(
                    deleted='').filter(title__icontains=title)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and deleted == '' and withdrawal == '' and category == '' and title == '':
                print("done28")
                obj = books.objects.all().filter(dates__range=(start_date, end_date)).filter(withdrawal_no='').filter(
                    deleted='')
                return render(request, 'report.html', {'query_results': obj})



            elif category != '' and start_date == '' and end_date == '' and deleted == '' and withdrawal == '' and title == '':
                print("done29")
                obj = books.objects.all().filter(category__icontains=category).filter(withdrawal_no='').filter(
                    deleted='')
                return render(request, 'report.html', {'query_results': obj})
            elif title != '' and start_date == '' and end_date == '' and deleted == '' and withdrawal == '' and category == '':
                print("done30")
                obj = books.objects.all().filter(title__icontains=title).filter(withdrawal_no='').filter(deleted='')
                return render(request, 'report.html', {'query_results': obj})
            elif title != '' and start_date == '' and end_date == '' and deleted == '' and withdrawal == '' and category != '':
                print("done31")
                obj = books.objects.all().filter(title__icontains=title).filter(category__icontains=category).filter(
                    withdrawal_no='').filter(deleted='')
                return render(request, 'report.html', {'query_results': obj})


            elif start_date == '' and end_date == '' and deleted == '' and withdrawal == '' and category == '' and title == '':
                print("done32")
                obj = books.objects.all().filter(withdrawal_no='').filter(deleted='')
                return render(request, 'report.html', {'query_results': obj})



        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in list")
            return render(request, 'list.html')
    else:
        return render(request, 'list.html')


def issue_register_s(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        date1 = request.POST.get("date", "")
        month = request.POST.get("month", "")
        title = request.POST.get("title", "")
        year = request.POST.get("year", "")

        try:
            if date1 != '' and month != '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                        issue_date__month=month,
                                                                                        issue_date__day=date1).filter(
                    ~Q(std_name='')).order_by('issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    title__icontains=title).filter(~Q(std_name='')).order_by('issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year).filter(
                    title__icontains=title).filter(~Q(std_name='')).order_by('issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(~Q(std_name='')).order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month,
                                                         issue_date__day=date1).filter(~Q(std_name='')).order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__month=month, issue_date__day=date1).filter(
                    ~Q(std_name='')).order_by('issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__day=date1).filter(~Q(std_name='')).order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__year=year, issue_date__day=date1).filter(~Q(std_name='')).order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__day=date1).filter(~Q(std_name='')).order_by('issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month, issue_date__day=date1).filter(~Q(std_name='')).order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month).filter(~Q(std_name='')).order_by('issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                        date_of_receipt__day=date1).filter(
                    ~Q(std_name='')).order_by('issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year).filter(~Q(std_name='')).order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__month=month).filter(~Q(std_name='')).order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__day=date1).filter(
                    ~Q(std_name='')).order_by('issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    ~Q(std_name='')).order_by('issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '':
                ver3 = manage_books.objects.all().order_by('issue_date').reverse().filter(~Q(std_name=''))
                return render(request, 'issue_return.html', {'query_results': ver3})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in list")
            return render(request, 'list6.html')
    else:
        ver3 = manage_books.objects.all().order_by('issue_date').reverse().filter(~Q(std_name=''))
        return render(request, 'issue_return.html', {'query_results': ver3})


def issue_register_e(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        date1 = request.POST.get("date", "")
        month = request.POST.get("month", "")
        title = request.POST.get("title", "")
        year = request.POST.get("year", "")

        try:
            if date1 != '' and month != '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                        issue_date__month=month,
                                                                                        issue_date__day=date1).filter(
                    ~Q(emp_name='')).order_by('issue_date').reverse()
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    title__icontains=title).filter(~Q(emp_name='')).order_by('issue_date').reverse()
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year).filter(
                    title__icontains=title).filter(~Q(emp_name='')).order_by('issue_date').reverse()
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(~Q(emp_name='')).order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month,
                                                         issue_date__day=date1).filter(~Q(emp_name='')).order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__month=month, issue_date__day=date1).filter(
                    ~Q(emp_name='')).order_by('issue_date').reverse()
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__day=date1).filter(~Q(emp_name='')).order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__year=year, issue_date__day=date1).filter(~Q(emp_name='')).order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__day=date1).filter(~Q(emp_name='')).order_by('issue_date').reverse()
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month, issue_date__day=date1).filter(~Q(emp_name='')).order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month).filter(~Q(emp_name='')).order_by('issue_date').reverse()
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                        date_of_receipt__day=date1).filter(
                    ~Q(emp_name='')).order_by('issue_date').reverse()
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year).filter(~Q(emp_name='')).order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__month=month).filter(~Q(emp_name='')).order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__day=date1).filter(
                    ~Q(emp_name='')).order_by('issue_date').reverse()
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    ~Q(emp_name='')).order_by('issue_date').reverse()
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '':
                ver3 = manage_books.objects.all().order_by('issue_date').reverse().filter(~Q(emp_name=''))
                return render(request, 'issue_return1.html', {'query_results': ver3})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in list")
            return render(request, 'list8.html')
    else:
        ver3 = manage_books.objects.all().order_by('issue_date').reverse().filter(~Q(emp_name=''))
        return render(request, 'issue_return1.html', {'query_results': ver3})


def withdraw_register(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        date1 = request.POST.get("date", "")
        month = request.POST.get("month", "")
        title = request.POST.get("title", "")
        year = request.POST.get("year", "")

        try:
            if date1 != '' and month != '' and year != '' and title != '':
                ver3 = books.objects.all().filter(title__icontains=title).filter(withdrawal_date__year=year,
                                                                                 withdrawal_date__month=month,
                                                                                 withdrawal_date__day=date1).filter(
                    ~Q(withdrawal_no='')).order_by('withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title != '':
                ver3 = books.objects.all().filter(withdrawal_date__year=year, withdrawal_date__month=month).filter(
                    title__icontains=title).filter(~Q(withdrawal_no='')).order_by('withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = books.objects.all().filter(withdrawal_date__year=year).filter(
                    title__icontains=title).filter(~Q(withdrawal_no='')).order_by('withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title != '':
                ver3 = books.objects.all().filter(title__icontains=title).filter(~Q(withdrawal_no='')).order_by(
                    'withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year != '' and title == '':
                ver3 = books.objects.all().filter(withdrawal_date__year=year, withdrawal_date__month=month,
                                                  withdrawal_date__day=date1).filter(~Q(withdrawal_no='')).order_by(
                    'withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title == '':
                ver3 = books.objects.all().filter(withdrawal_date__month=month, withdrawal_date__day=date1).filter(
                    ~Q(withdrawal_no='')).order_by('withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title == '':
                ver3 = books.objects.all().filter(withdrawal_date__day=date1).filter(~Q(withdrawal_no='')).order_by(
                    'withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title != '':
                ver3 = books.objects.all().filter(title__icontains=title).filter(
                    withdrawal_date__year=year, withdrawal_date__day=date1).filter(~Q(withdrawal_no='')).order_by(
                    'withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title != '':
                ver3 = books.objects.all().filter(title__icontains=title).filter(
                    withdrawal_date__day=date1).filter(~Q(withdrawal_no='')).order_by('withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title != '':
                ver3 = books.objects.all().filter(title__icontains=title).filter(
                    withdrawal_date__month=month, withdrawal_date__day=date1).filter(~Q(withdrawal_no='')).order_by(
                    'withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title != '':
                ver3 = books.objects.all().filter(title__icontains=title).filter(
                    withdrawal_date__month=month).filter(~Q(withdrawal_no='')).order_by('withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = books.objects.all().filter(title__icontains=title).filter(withdrawal_date__year=year,
                                                                                 date_of_receipt__day=date1).filter(
                    ~Q(withdrawal_no='')).order_by('withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title == '':
                ver3 = books.objects.all().filter(withdrawal_date__year=year).filter(~Q(withdrawal_no='')).order_by(
                    'withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title == '':
                ver3 = books.objects.all().filter(withdrawal_date__month=month).filter(~Q(withdrawal_no='')).order_by(
                    'withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title == '':
                ver3 = books.objects.all().filter(withdrawal_date__year=year, withdrawal_date__day=date1).filter(
                    ~Q(withdrawal_no='')).order_by('withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title == '':
                ver3 = books.objects.all().filter(withdrawal_date__year=year, withdrawal_date__month=month).filter(
                    ~Q(withdrawal_no='')).order_by('withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '':
                ver3 = books.objects.all().order_by('withdrawal_date').reverse().filter(~Q(withdrawal_no=''))
                return render(request, 'report.html', {'query_results': ver3})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in list")
            return render(request, 'list12.html')
    else:
        return render(request, 'list12.html')


def journal_register(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        date1 = request.POST.get("date", "")
        month = request.POST.get("month", "")
        title = request.POST.get("title", "")
        year = request.POST.get("year", "")

        try:
            if date1 != '' and month != '' and year != '' and title != '':
                ver3 = newspaper.objects.all().filter(type='Journal').filter(title__icontains=title).filter(
                    date_of_receipt__year=year, date_of_receipt__month=month, date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title != '':
                ver3 = newspaper.objects.all().filter(type='Journal').filter(date_of_receipt__year=year,
                                                                      date_of_receipt__month=month).filter(
                    title__icontains=title).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = newspaper.objects.all().filter(type='Journal').filter(date_of_receipt__year=year).filter(
                    title__icontains=title).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title != '':
                ver3 = newspaper.objects.all().filter(type='Journal').filter(title__icontains=title).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year != '' and title == '':
                ver3 = newspaper.objects.all().filter(type='Journal').filter(date_of_receipt__year=year,
                                                                      date_of_receipt__month=month,
                                                                      date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title == '':
                ver3 = newspaper.objects.all().filter(type='Journal').filter(date_of_receipt__month=month,
                                                                      date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title == '':
                ver3 = newspaper.objects.all().filter(type='Journal').filter(date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title != '':
                ver3 = newspaper.objects.all().filter(type='Journal').filter(title__icontains=title).filter(
                    date_of_receipt__year=year, date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title != '':
                ver3 = newspaper.objects.all().filter(type='Journal').filter(title__icontains=title).filter(
                    date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title != '':
                ver3 = newspaper.objects.all().filter(type='Journal').filter(title__icontains=title).filter(
                    date_of_receipt__month=month, date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title != '':
                ver3 = newspaper.objects.all().filter(type='Journal').filter(title__icontains=title).filter(
                    date_of_receipt__month=month).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = newspaper.objects.all().filter(type='Journal').filter(title__icontains=title).filter(
                    date_of_receipt__month=month, date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title == '':
                ver3 = newspaper.objects.all().filter(type='Journal').filter(date_of_receipt__year=year).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title == '':
                ver3 = newspaper.objects.all().filter(type='Journal').filter(date_of_receipt__month=month).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title == '':
                ver3 = newspaper.objects.all().filter(type='Journal').filter(date_of_receipt__year=year,
                                                                      date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title == '':
                ver3 = newspaper.objects.all().filter(type='Journal').filter(date_of_receipt__year=year,
                                                                      date_of_receipt__month=month).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '':
                ver3 = newspaper.objects.all().filter(type='Journal').order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in list")
            return render(request, 'list3.html')
    else:
        return render(request, 'list3.html')

def newspaper_register(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        date1 = request.POST.get("date", "")
        month = request.POST.get("month", "")
        title = request.POST.get("title", "")
        year = request.POST.get("year", "")

        try:
            if date1!='' and month!='' and year!=''and title!='':
                ver3 = newspaper.objects.all().filter(type='').filter(title__icontains=title).filter(date_of_receipt__year=year, date_of_receipt__month=month, date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_newspaper.html', {'query_results': ver3})
            elif  date1=='' and month!='' and year!=''and title!='':
                ver3 = newspaper.objects.all().filter(type='').filter(date_of_receipt__year=year, date_of_receipt__month=month).filter(title__icontains=title).order_by('date_of_receipt').reverse()
                return render(request, 'r_newspaper.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = newspaper.objects.all().filter(type='').filter(date_of_receipt__year=year).filter(title__icontains=title).order_by('date_of_receipt').reverse()
                return render(request, 'r_newspaper.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title != '':
                ver3 = newspaper.objects.all().filter(type='').filter(title__icontains=title).order_by('date_of_receipt').reverse()
                return render(request, 'r_newspaper.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year != '' and title == '':
                ver3 = newspaper.objects.all().filter(type='').filter(date_of_receipt__year=year,date_of_receipt__month=month, date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_newspaper.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title == '':
                ver3 = newspaper.objects.all().filter(type='').filter(date_of_receipt__month=month, date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_newspaper.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title == '':
                ver3 = newspaper.objects.all().filter(type='').filter(date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_newspaper.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title != '':
                ver3 = newspaper.objects.all().filter(type='').filter(title__icontains=title).filter(date_of_receipt__year=year, date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_newspaper.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title != '':
                ver3 = newspaper.objects.all().filter(type='').filter(title__icontains=title).filter(date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_newspaper.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title != '':
                ver3 = newspaper.objects.all().filter(type='').filter(title__icontains=title).filter(date_of_receipt__month=month,date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_newspaper.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title != '':
                ver3 = newspaper.objects.all().filter(type='').filter(title__icontains=title).filter(date_of_receipt__month=month).order_by('date_of_receipt').reverse()
                return render(request, 'r_newspaper.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = newspaper.objects.all().filter(type='').filter(title__icontains=title).filter(date_of_receipt__month=month,date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_newspaper.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title == '':
                ver3 = newspaper.objects.all().filter(type='').filter(date_of_receipt__year=year).order_by('date_of_receipt').reverse()
                return render(request, 'r_newspaper.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title == '':
                ver3 = newspaper.objects.all().filter(type='').filter(date_of_receipt__month=month).order_by('date_of_receipt').reverse()
                return render(request, 'r_newspaper.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title == '':
                ver3 = newspaper.objects.all().filter(type='').filter(date_of_receipt__year=year, date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_newspaper.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title == '':
                ver3 = newspaper.objects.all().filter(type='').filter(date_of_receipt__year=year, date_of_receipt__month=month).order_by('date_of_receipt').reverse()
                return render(request, 'r_newspaper.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '':
                ver3 = newspaper.objects.all().filter(type='').order_by('date_of_receipt').reverse()
                return render(request, 'r_newspaper.html', {'query_results': ver3})
        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in list")
            return render(request, 'list1.html')
    else:
        return render(request, 'list1.html')

def magazine_register(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        date1 = request.POST.get("date", "")
        month = request.POST.get("month", "")
        title = request.POST.get("title", "")
        year = request.POST.get("year", "")

        try:
            if date1 != '' and month != '' and year != '' and title != '':
                ver3 = newspaper.objects.all().filter(type='Magazine').filter(title__icontains=title).filter(
                    date_of_receipt__year=year, date_of_receipt__month=month, date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title != '':
                ver3 = newspaper.objects.all().filter(type='Magazine').filter(date_of_receipt__year=year,
                                                                      date_of_receipt__month=month).filter(
                    title__icontains=title).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = newspaper.objects.all().filter(type='Magazine').filter(date_of_receipt__year=year).filter(
                    title__icontains=title).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title != '':
                ver3 = newspaper.objects.all().filter(type='Magazine').filter(title__icontains=title).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year != '' and title == '':
                ver3 = newspaper.objects.all().filter(type='Magazine').filter(date_of_receipt__year=year,
                                                                      date_of_receipt__month=month,
                                                                      date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title == '':
                ver3 = newspaper.objects.all().filter(type='Magazine').filter(date_of_receipt__month=month,
                                                                      date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title == '':
                ver3 = newspaper.objects.all().filter(type='Magazine').filter(date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title != '':
                ver3 = newspaper.objects.all().filter(type='Magazine').filter(title__icontains=title).filter(
                    date_of_receipt__year=year, date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title != '':
                ver3 = newspaper.objects.all().filter(type='Magazine').filter(title__icontains=title).filter(
                    date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title != '':
                ver3 = newspaper.objects.all().filter(type='Magazine').filter(title__icontains=title).filter(
                    date_of_receipt__month=month, date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title != '':
                ver3 = newspaper.objects.all().filter(type='Magazine').filter(title__icontains=title).filter(
                    date_of_receipt__month=month).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = newspaper.objects.all().filter(type='Magazine').filter(title__icontains=title).filter(
                    date_of_receipt__month=month, date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title == '':
                ver3 = newspaper.objects.all().filter(type='Magazine').filter(date_of_receipt__year=year).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title == '':
                ver3 = newspaper.objects.all().filter(type='Magazine').filter(date_of_receipt__month=month).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title == '':
                ver3 = newspaper.objects.all().filter(type='Magazine').filter(date_of_receipt__year=year,
                                                                      date_of_receipt__day=date1).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title == '':
                ver3 = newspaper.objects.all().filter(type='Magazine').filter(date_of_receipt__year=year,
                                                                      date_of_receipt__month=month).order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '':
                ver3 = newspaper.objects.all().filter(type='Magazine').order_by('date_of_receipt').reverse()
                return render(request, 'r_journal.html', {'query_results': ver3})
        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in list")
            return render(request, 'list2.html')
    else:
        return render(request, 'list2.html')


def return_register_s(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        date1 = request.POST.get("date", "")
        month = request.POST.get("month", "")
        title = request.POST.get("title", "")
        year = request.POST.get("year", "")

        try:
            if date1 != '' and month != '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                        issue_date__month=month,
                                                                                        issue_date__day=date1).filter(
                    ~Q(std_name='')).filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    title__icontains=title).filter(~Q(std_name='')).filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year).filter(
                    title__icontains=title).filter(~Q(std_name='')).filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(~Q(std_name='')).filter(
                    returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month,
                                                         issue_date__day=date1).filter(~Q(std_name='')).filter(
                    returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__month=month, issue_date__day=date1).filter(
                    ~Q(std_name='')).filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__day=date1).filter(~Q(std_name='')).filter(
                    returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__year=year, issue_date__day=date1).filter(~Q(std_name='')).filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__day=date1).filter(~Q(std_name='')).filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month, issue_date__day=date1).filter(~Q(std_name='')).filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month).filter(~Q(std_name='')).filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                        date_of_receipt__day=date1).filter(
                    ~Q(std_name='')).filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year).filter(~Q(std_name='')).filter(
                    returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__month=month).filter(~Q(std_name='')).filter(
                    returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__day=date1).filter(
                    ~Q(std_name='')).filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    ~Q(std_name='')).filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '':
                ver3 = manage_books.objects.all().order_by('issue_date').reverse().filter(~Q(std_name='')).filter(
                    returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in list")
            return render(request, 'list7.html')
    else:
        return render(request, 'list7.html')


def return_register_e(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        date1 = request.POST.get("date", "")
        month = request.POST.get("month", "")
        title = request.POST.get("title", "")
        year = request.POST.get("year", "")

        try:
            if date1 != '' and month != '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                        issue_date__month=month,
                                                                                        issue_date__day=date1).filter(
                    ~Q(emp_name='')).filter(returned='yes')
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    title__icontains=title).filter(~Q(emp_name='')).filter(returned='yes')
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year).filter(
                    title__icontains=title).filter(~Q(emp_name='')).filter(returned='yes')
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(~Q(emp_name='')).filter(
                    returned='yes')
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month,
                                                         issue_date__day=date1).filter(~Q(emp_name='')).filter(
                    returned='yes')
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__month=month, issue_date__day=date1).filter(
                    ~Q(emp_name='')).filter(returned='yes')
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__day=date1).filter(~Q(emp_name='')).filter(
                    returned='yes')
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__year=year, issue_date__day=date1).filter(~Q(emp_name='')).filter(returned='yes')
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__day=date1).filter(~Q(emp_name='')).filter(returned='yes')
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month, issue_date__day=date1).filter(~Q(emp_name='')).filter(returned='yes')
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month).filter(~Q(emp_name='')).filter(returned='yes')
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                        date_of_receipt__day=date1).filter(
                    ~Q(emp_name='')).filter(returned='yes')
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year).filter(~Q(emp_name='')).filter(
                    returned='yes')
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__month=month).filter(~Q(emp_name='')).filter(
                    returned='yes')
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__day=date1).filter(
                    ~Q(emp_name='')).filter(returned='yes')
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    ~Q(emp_name='')).filter(returned='yes')
                return render(request, 'issue_return1.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '':
                ver3 = manage_books.objects.all().order_by('issue_date').reverse().filter(~Q(emp_name='')).filter(
                    returned='yes')
                return render(request, 'issue_return1.html', {'query_results': ver3})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in list")
            return render(request, 'list9.html')
    else:
        return render(request, 'list9.html')


def over_due_s(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        date1 = request.POST.get("date", "")
        month = request.POST.get("month", "")
        title = request.POST.get("title", "")
        year = request.POST.get("year", "")

        try:
            if date1 != '' and month != '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                        issue_date__month=month,
                                                                                        issue_date__day=date1).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(std_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    title__icontains=title).filter(due_date__lt=datetime.date.today()).filter(returned='no').order_by(
                    'issue_date').reverse().filter(~Q(std_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year).filter(
                    title__icontains=title).filter(due_date__lt=datetime.date.today()).filter(returned='no').order_by(
                    'issue_date').reverse().filter(~Q(std_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(std_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month,
                                                         issue_date__day=date1).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(std_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__month=month, issue_date__day=date1).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(std_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__day=date1).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(std_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__year=year, issue_date__day=date1).filter(due_date__lt=datetime.date.today()).filter(
                    returned='no').order_by('issue_date').reverse().filter(~Q(std_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__day=date1).filter(due_date__lt=datetime.date.today()).filter(returned='no').order_by(
                    'issue_date').reverse().filter(~Q(std_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month, issue_date__day=date1).filter(due_date__lt=datetime.date.today()).filter(
                    returned='no').order_by('issue_date').reverse().filter(~Q(std_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month).filter(due_date__lt=datetime.date.today()).filter(returned='no').order_by(
                    'issue_date').reverse().filter(~Q(std_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                        date_of_receipt__day=date1).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(std_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(std_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__month=month).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(std_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__day=date1).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(std_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(std_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '':
                ver3 = manage_books.objects.all().order_by('issue_date').reverse().filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').filter(~Q(std_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in list")
            return render(request, 'list10.html')
    else:
        ver3 = manage_books.objects.all().order_by('issue_date').reverse().filter(
            due_date__lt=datetime.date.today()).filter(returned='no').filter(~Q(std_name=''))
        return render(request, 'issue_return2.html', {'query_results': ver3})


def pending_reg_s(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        date1 = request.POST.get("date", "")
        month = request.POST.get("month", "")
        title = request.POST.get("title", "")
        year = request.POST.get("year", "")
        accession_id = request.POST.get("accession_id", "")

        try:
            if date1 != '' and month != '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                        issue_date__month=month,
                                                                                        issue_date__day=date1).filter(
                    returned='no').order_by('issue_date').reverse().filter(~Q(std_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    title__icontains=title).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(std_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year).filter(
                    title__icontains=title).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(std_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(returned='no').order_by(
                    'issue_date').reverse().filter(~Q(std_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month,
                                                         issue_date__day=date1).filter(returned='no').order_by(
                    'issue_date').reverse().filter(~Q(std_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__month=month, issue_date__day=date1).filter(
                    returned='no').order_by('issue_date').reverse().filter(~Q(std_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__day=date1).filter(returned='no').order_by(
                    'issue_date').reverse().filter(~Q(std_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__year=year, issue_date__day=date1).filter(returned='no').order_by(
                    'issue_date').reverse().filter(~Q(std_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__day=date1).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(std_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month, issue_date__day=date1).filter(returned='no').order_by(
                    'issue_date').reverse().filter(~Q(std_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(std_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                        date_of_receipt__day=date1).filter(
                    returned='no').order_by('issue_date').reverse().filter(~Q(std_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year).filter(returned='no').order_by(
                    'issue_date').reverse().filter(~Q(std_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__month=month).filter(returned='no').order_by(
                    'issue_date').reverse().filter(~Q(std_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__day=date1).filter(
                    returned='no').order_by('issue_date').reverse().filter(~Q(std_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    returned='no').order_by('issue_date').reverse().filter(~Q(std_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '' and accession_id!='':
                ver3 = manage_books.objects.all().order_by('issue_date').reverse().filter(returned='no').filter(
                    ~Q(std_name='')).filter(accession_id=accession_id)
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '':
                ver3 = manage_books.objects.all().order_by('issue_date').reverse().filter(returned='no').filter(
                    ~Q(std_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in list")
            return render(request, 'list11.html')
    else:
        '''ver3 = manage_books.objects.all().order_by('issue_date').reverse().filter(returned='no').filter(
            ~Q(std_name=''))
        return render(request, 'issue_return3.html', {'query_results': ver3})'''
        return render(request, 'list11.html')


def over_due_e(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        date1 = request.POST.get("date", "")
        month = request.POST.get("month", "")
        title = request.POST.get("title", "")
        year = request.POST.get("year", "")

        try:
            if date1 != '' and month != '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                        issue_date__month=month,
                                                                                        issue_date__day=date1).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(emp_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    title__icontains=title).filter(due_date__lt=datetime.date.today()).filter(returned='no').order_by(
                    'issue_date').reverse().filter(~Q(emp_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year).filter(
                    title__icontains=title).filter(due_date__lt=datetime.date.today()).filter(returned='no').order_by(
                    'issue_date').reverse().filter(~Q(emp_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(emp_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month,
                                                         issue_date__day=date1).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(emp_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__month=month, issue_date__day=date1).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(emp_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__day=date1).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(emp_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__year=year, issue_date__day=date1).filter(due_date__lt=datetime.date.today()).filter(
                    returned='no').order_by('issue_date').reverse().filter(~Q(emp_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__day=date1).filter(due_date__lt=datetime.date.today()).filter(returned='no').order_by(
                    'issue_date').reverse().filter(~Q(emp_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month, issue_date__day=date1).filter(due_date__lt=datetime.date.today()).filter(
                    returned='no').order_by('issue_date').reverse().filter(~Q(emp_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month).filter(due_date__lt=datetime.date.today()).filter(returned='no').order_by(
                    'issue_date').reverse().filter(~Q(emp_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                        date_of_receipt__day=date1).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(emp_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(emp_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__month=month).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(emp_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__day=date1).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(emp_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(emp_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '':
                ver3 = manage_books.objects.all().order_by('issue_date').reverse().filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').filter(~Q(emp_name=''))
                return render(request, 'issue_return2.html', {'query_results': ver3})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in list")
            return render(request, 'list13.html')
    else:
        ver3 = manage_books.objects.all().order_by('issue_date').reverse().filter(
            due_date__lt=datetime.date.today()).filter(returned='no').filter(~Q(emp_name=''))
        return render(request, 'issue_return2.html', {'query_results': ver3})


def pending_reg_e(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        date1 = request.POST.get("date", "")
        month = request.POST.get("month", "")
        title = request.POST.get("title", "")
        year = request.POST.get("year", "")
        accession_id = request.POST.get("accession_id", "")

        try:
            if date1 != '' and month != '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                        issue_date__month=month,
                                                                                        issue_date__day=date1).filter(
                    returned='no').order_by('issue_date').reverse().filter(~Q(emp_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    title__icontains=title).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(emp_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year).filter(
                    title__icontains=title).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(emp_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(returned='no').order_by(
                    'issue_date').reverse().filter(~Q(emp_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month,
                                                         issue_date__day=date1).filter(returned='no').order_by(
                    'issue_date').reverse().filter(~Q(emp_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__month=month, issue_date__day=date1).filter(
                    returned='no').order_by('issue_date').reverse().filter(~Q(emp_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__day=date1).filter(returned='no').order_by(
                    'issue_date').reverse().filter(~Q(emp_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__year=year, issue_date__day=date1).filter(returned='no').order_by(
                    'issue_date').reverse().filter(~Q(emp_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__day=date1).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(emp_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month, issue_date__day=date1).filter(returned='no').order_by(
                    'issue_date').reverse().filter(~Q(emp_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month).filter(returned='no').order_by('issue_date').reverse().filter(
                    ~Q(emp_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_books.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                        date_of_receipt__day=date1).filter(
                    returned='no').order_by('issue_date').reverse().filter(~Q(emp_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year).filter(returned='no').order_by(
                    'issue_date').reverse().filter(~Q(emp_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__month=month).filter(returned='no').order_by(
                    'issue_date').reverse().filter(~Q(emp_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__day=date1).filter(
                    returned='no').order_by('issue_date').reverse().filter(~Q(emp_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title == '':
                ver3 = manage_books.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    returned='no').order_by('issue_date').reverse().filter(~Q(emp_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '' and accession_id!='':
                ver3 = manage_books.objects.all().order_by('issue_date').reverse().filter(returned='no').filter(
                    ~Q(emp_name='')).filter(accession_id=accession_id)
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '':
                ver3 = manage_books.objects.all().order_by('issue_date').reverse().filter(returned='no').filter(
                    ~Q(emp_name=''))
                return render(request, 'issue_return3.html', {'query_results': ver3})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in list")
            return render(request, 'list14.html')
    else:
        '''ver3 = manage_books.objects.all().order_by('issue_date').reverse().filter(returned='no').filter(
            ~Q(emp_name=''))
        return render(request, 'issue_return3.html', {'query_results': ver3})'''
        return render(request, 'list14.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST.get("username", "")
        name = request.POST.get("name", "")
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        password1 = request.POST.get("password1", "")

        if len(username) > 10:
            messages.error(request, "username must be under 10 characters")
            return redirect("/")
        if not username.isalnum():
            messages.error(request, "username should only contain letters and numbers")
            return redirect("/")
        if password != password1:
            messages.error(request, "password does not match")
            return redirect("/")
        myuser = User.objects.create_user(username, email, password)
        myuser.name = name
        myuser.save()
        messages.success(request, "your account has been successfully created")
        return redirect("/")
    return HttpResponse('404 - NOT fOUNT')


def handle_login(request):
    if request.method == 'POST':

        login_name = request.POST.get("Email", "")
        passwrd = request.POST.get("psw", "")
        user = authenticate(username=login_name, password=passwrd)
        if user is not None:

            login(request, user)
            messages.success(request, "successfully logged in")
            return redirect("/main")

        else:
            messages.error(request, "Invalid credentails ,Please try Again")
            print('error')
            return redirect("/")
    return HttpResponse('404 - Not Found')


def main(request):
    return render(request, 'nav.html')


def handle_logout(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, "Successfuly logged out")
        print("logged out")
        return redirect('/')

    return HttpResponse('404 - Not Found')


def notification(request):
    def msg(msg1, phn):
        msg2 = msg1
        phn_no = phn
        url = "https://www.fast2sms.com/dev/bulk"

        querystring = {
            "authorization": " C16QoaWfeOkvMsm7NJbhAqjzIXi40rpY9VxHUtgynFuwDELSPTzHLV2nRbi98caMtWqNUIyuemo417jQ ",
            "sender_id": "FSTSMS", "message": msg2, "language": "english", "route": "p", "numbers": phn_no}

        headers = {'cache-control': "no-cache"}

        response = requests.request("GET", url, headers=headers, params=querystring)

        print(response.text)

    ver2 = manage_books.objects.all()
    print(ver2)
    for i in ver2:
        day = datetime.date.today()
        stored_day = i.return_date
        b = stored_day.day - day.day
        if b == 2:
            print("pending days are two")
            m = "Two days left to return book"
            ph = 8872183132
            msg(m, ph)
        elif b == 1:
            print("pending days are one")
            m = "One day left to return book"
            ph = 8872183132
            msg(m, ph)
        elif b == 0:
            print("today is last day")
            m = "Today is last day  to return book"
            ph = 8872183132
            msg(m, ph)

    return render(request, 'notify.html')


def add_bookbank(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        dates = request.POST.get("dates", "")

        title = request.POST.get("title", "")
        author = request.POST.get("author", "")
        classification = request.POST.get("classification", "")
        volume = request.POST.get("volume", "")
        publisher = request.POST.get("publisher", "")
        category = request.POST.get('category', "")
        yearPublication = request.POST.get("yearPublication", "")
        no_pages = request.POST.get("no_pages", "")
        purchased_from = request.POST.get("purchased_from", "")
        bill_no = request.POST.get("bill_no", "")
        bill_date = request.POST.get("bill_date", "")
        cost = request.POST.get("cost", "")
        edition = request.POST.get("edition", "")
        copies = request.POST.get("copies", "")
        ver = bookbank.objects.all().last()

        request.session['copies'] = copies

        accession_no = ver.accession_number
        print(accession_no)
        x = accession_no.split(".")
        asc_no = 'BB.' + str(int(x[1]) + 1)

        request.session['accession1'] = asc_no
        print("acsno", asc_no)

        if dates == '':
            dates = datetime.date.today()
            print(dates)

        try:

            if category == 'select':
                messages.error(request, "select category")
                return redirect('/add_bookbank')
            elif copies == '0':
                messages.error(request, "Number of Copies can't be 0")
                return redirect('/add_bookbank')


            else:
                for j in range(0, int(copies)):
                    print("copies are", copies)

                    print("done1")
                    sig = bookbank(accession_number=asc_no, dates=dates, title=title, author=author,
                                   classification=classification, publisher=publisher, category=category,
                                   yearPublication=yearPublication, no_pages=no_pages, purchased_from=purchased_from,
                                   bill_no=bill_no, bill_date=bill_date, cost=cost, edition=edition, copies=copies,
                                   volume=volume)
                    print('done2')

                    sig.save()
                    print("done3")
                    print('done4', asc_no)
                    print(type(asc_no))
                    x = asc_no.split(".")
                    print(x)
                    print(x[1])
                    asc_no = 'BB.' + str(int(x[1]) + 1)
                    print("book added")
                messages.error(request, "Book Added successfully")
                return redirect('/add_bookbank')
        except:
            print("error")
            messages.error(request, "Enter valid data,Please try again")
            return redirect('/add_bookbank')
    ver = bookbank.objects.all().last()
    accession_no = ver.accession_number
    print(accession_no)
    x = accession_no.split(".")

    return render(request, 'bookbank_master.html', {'id': 'BB.' + str(int(x[1]) + 1)})


def qr_gen_bb(request):
    if not request.user.is_authenticated:
        return redirect("/")
    try:
        list = []
        accession_no = request.session['accession1']

        copies = int(request.session['copies'])
        for i in range(0, copies):
            hr = barcode.get_barcode_class('code128')
            qr = hr(accession_no, writer=ImageWriter())
            a = qr.save(r'C:\Users\OfficePC\PycharmProjects\mindlinks\library\static/' + accession_no)
            print(accession_no)
            qr_name = accession_no + '.png'
            list.append(qr_name)
            print(list)
            x = accession_no.split(".")

            accession_no = 'BB.' + str(int(x[1]) + 1)
            # accession_no += 1
        return render(request, 'barcode.html', {'list': list})
    except:
        messages.error(request, "There are some Errors!!Please try again")
        print("There are some Errors!!Please try again")
        return render(request, 'barcode.html')


def click_d_bb(request):
    i = 0
    cap = cv2.VideoCapture(0)
    while i < 1:
        _, frame = cap.read()
        decoded = pyzbar.decode(frame)
        for obj in decoded:
            print(obj)
            a = obj.data.decode("ascii")
            b = str(a)
            print("the code is:", a)
            request.session['id1'] = b
            i = i + 1
            return render(request, 'Delete_Bookbank.html', {'param': b})
        cv2.imshow("qrcode", frame)
        cv2.waitKey(100)
        cv2.destroyAllWindows()
    return redirect('/delete_bookbank')


def get_d_bb(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        accession_no = request.POST.get("accession_no", "")
        try:
            if accession_no == '':
                accession_no = request.session['id1']
            request.session['id1'] = accession_no

            ver = bookbank.objects.get(accession_number=accession_no)
            if ver.deleted == "deleted":
                messages.error(request, "Already Deleted")
                return render(request, 'delete_bb.html')
            else:

                return render(request, 'delete_bb.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category,
                               "yearPublication": ver.yearPublication, "no_pages": ver.no_pages, "cost": ver.cost,
                               "edition": ver.edition, "volume": ver.volume})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            return render(request, 'delete_bb.html')
    return render(request, 'Delete_Bookbank.html')


def delete_bookbank(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        accession_no = request.POST.get("accession_no", "")
        try:
            if accession_no == '':
                accession_no = request.session['id1']
            ver = bookbank.objects.get(accession_number=accession_no)
            ver.deleted = "deleted"
            ver.save()
            messages.error(request, "Book deleted Successfully")
            print("delete done")
            return render(request, 'Delete_Bookbank.html')
        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in delete")
            return render(request, 'Delete_Bookbank.html')
    else:
        return render(request, 'Delete_Bookbank.html', )


def click_w_bb(request):
    i = 0
    cap = cv2.VideoCapture(0)
    while i < 1:
        _, frame = cap.read()
        decoded = pyzbar.decode(frame)
        for obj in decoded:
            print(obj)
            a = obj.data.decode("ascii")
            b = str(a)
            print("the code is:", a)
            request.session['id1'] = b
            i = i + 1
            return render(request, 'withdrawal_bb.html', {'param': b})
        cv2.imshow("qrcode", frame)
        cv2.waitKey(100)
        cv2.destroyAllWindows()
    return redirect('/withdrawal_bookbank')


def get_d_w_b(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        accession_no = request.POST.get("accession_no", "")
        dates = request.POST.get("dates", "")
        request.session['id2'] = dates
        try:
            if accession_no == '':
                accession_no = request.session['id1']
            request.session['id1'] = accession_no

            ver = bookbank.objects.get(accession_number=accession_no)
            if ver.withdrawal_no != "":
                messages.error(request, "Already Write Off")
                return render(request, 'delete_w_b.html')
            else:

                return render(request, 'delete_w_b.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category,
                               "yearPublication": ver.yearPublication, "no_pages": ver.no_pages, "cost": ver.cost,
                               "edition": ver.edition, "volume": ver.volume})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            return render(request, 'delete_w_b.html')
    return render(request, 'withdrawal_bb.html')


def withdrawal_bookbank(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        accession_no = request.POST.get("accession_no", "")
        dates = request.session['id2']
        ver = bookbank.objects.all().filter(~Q(withdrawal_no=''))
        wd_no = []
        for i in ver:
            wd_no.append(i.withdrawal_no)
        abc = max(wd_no)
        try:
            if accession_no == '':
                accession_no = request.session['id1']
            ver = bookbank.objects.get(accession_number=accession_no)
            ver.withdrawal_no = int(abc) + 1
            ver.withdrawal_date = dates
            ver.save()
            messages.error(request, "Book withdrawal Successfully")

            return render(request, 'withdrawal_bb.html')
        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in delete")
            return render(request, 'withdrawal_bb.html')
    else:
        return render(request, 'withdrawal_bb.html', )


def click_u_bb(request):
    i = 0
    cap = cv2.VideoCapture(0)
    while i < 1:
        _, frame = cap.read()
        decoded = pyzbar.decode(frame)
        for obj in decoded:
            print(obj)
            a = obj.data.decode("ascii")
            b = str(a)
            print("the code is:", a)
            request.session['id1'] = b
            i = i + 1
            return render(request, 'notify_bb.html', {'param': b})
        cv2.imshow("qrcode", frame)
        cv2.waitKey(100)
        cv2.destroyAllWindows()

    return redirect('/get_u_bb')


def get_u_bb(request):
    if request.method == 'POST':
        accession_no = request.POST.get("accession_no", "")
        if accession_no == '':
            print("yse")
            accession_no = request.session['id1']

        request.session['id1'] = accession_no
        print("done")

        return redirect('/update_bookbank')

    return render(request, 'notify_bb.html')


def update_bookbank(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        title = request.POST.get('title', "")
        author = request.POST.get('author', "")
        classification = request.POST.get('classification', "")
        volume = request.POST.get('volume', "")
        publisher = request.POST.get('publisher', "")
        category = request.POST.get('category', "")
        yearpublication = request.POST.get('yearpublication', "")
        pages = request.POST.get('pages', "")
        cost = request.POST.get('cost', "")
        edition = request.POST.get('edition', "")
        bill_no = request.POST.get('bill_no', "")
        bill_date = request.POST.get('bill_date', "")
        dates = request.POST.get('dates', "")
        purchased_from = request.POST.get('purchased_from', "")

        accession_no = request.session['id1']

        try:

            if title != "":
                ver = bookbank.objects.get(accession_number=accession_no)
                ver.title = title
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'bookbank_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})
            elif author != "":
                ver = bookbank.objects.get(accession_number=accession_no)
                ver.author = author
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'bookbank_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})
            elif classification != "":
                ver = bookbank.objects.get(accession_number=accession_no)
                ver.classification = classification
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'bookbank_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})
            elif volume != "":
                ver = bookbank.objects.get(accession_number=accession_no)
                ver.volume = volume
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'bookbank_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})
            elif publisher != "":
                ver = bookbank.objects.get(accession_number=accession_no)
                ver.publisher = publisher
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'bookbank_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})
            elif category != "":
                ver = bookbank.objects.get(accession_number=accession_no)
                ver.category = category
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'bookbank_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})
            elif yearpublication != "":
                ver = bookbank.objects.get(accession_number=accession_no)
                ver.yearPublication = yearpublication
                ver.save()
                print("done")
                messages.error(request, "Book updated Successfully")
                return render(request, 'bookbank_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})
            elif pages != "":
                ver = bookbank.objects.get(accession_number=accession_no)
                ver.no_pages = pages
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'bookbank_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})
            elif cost != "":
                ver = bookbank.objects.get(accession_number=accession_no)
                ver.cost = cost
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'bookbank_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})
            elif bill_no != "":
                ver = bookbank.objects.get(accession_number=accession_no)
                ver.bill_no = bill_no
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'bookbank_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})
            elif edition != "":
                ver = bookbank.objects.get(accession_number=accession_no)
                ver.edition = edition
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'bookbank_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})
            elif bill_date != "":
                ver = bookbank.objects.get(accession_number=accession_no)
                ver.bill_date = bill_date
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'bookbank_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})
            elif dates != "":
                ver = bookbank.objects.get(accession_number=accession_no)
                ver.dates = dates
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'bookbank_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})
            elif purchased_from != "":
                ver = bookbank.objects.get(accession_number=accession_no)
                ver.purchased_from = purchased_from
                ver.save()
                messages.error(request, "Book updated Successfully")
                return render(request, 'bookbank_manage.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category, "yearPublication": ver.yearPublication,
                               "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                               "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                               "dates": ver.dates,
                               "purchased_from": ver.purchased_from})

            else:
                messages.error(request, "Enter valid data,Please try again ")
                return render(request, 'notify_bb.html')
        except:

            messages.error(request, "Enter valid data,Please try again")
            return render(request, 'bookbank_manage.html')
    else:
        try:
            accession_no = request.session['id1']
            ver = bookbank.objects.get(accession_number=accession_no)
            return render(request, 'bookbank_manage.html',
                          {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                           "classification": ver.classification, "publisher": ver.publisher,
                           "category": ver.category, "yearPublication": ver.yearPublication,
                           "no_pages": ver.no_pages, "cost": ver.cost, "edition": ver.edition,
                           "volume": ver.volume, "bill_no": ver.bill_no, "bill_date": ver.bill_date,
                           "dates": ver.dates,
                           "purchased_from": ver.purchased_from})
        except:

            return render(request, 'bookbank_manage.html')


def main_bb(request):
    return render(request, 'nav1.html')


def barcode_gen_bb(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        try:
            list = []
            accession_no = request.POST.get("start", "")

            x = accession_no.split(".")
            ab = int(x[1])
            accession_no = 'BB.' + str(int(x[1]))
            copies = request.POST.get("end", "")
            x1 = copies.split(".")
            cd = int(x1[1])

            n = cd - ab
            print(n)
            for i in range(0, n + 1):
                hr = barcode.get_barcode_class('code128')
                qr = hr(accession_no, writer=ImageWriter())
                a = qr.save(r'C:\Users\OfficePC\PycharmProjects\mindlinks\library\static/' + accession_no)
                print(accession_no)
                qr_name = accession_no + '.png'

                list.append(qr_name)
                print(list)
                x2 = accession_no.split(".")

                accession_no = 'BB.' + str(int(x2[1]) + 1)

                # accession_no += 1

            return render(request, 'barcode.html.', {'list': list})
        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in barcode")
            return render(request, 'Barcode_genrator_bb.html')
    return render(request, 'Barcode_genrator_bb.html')


def click_i_s_bb(request):
    i = 0
    cap = cv2.VideoCapture(0)
    while i < 1:
        _, frame = cap.read()
        decoded = pyzbar.decode(frame)
        for obj in decoded:
            print(obj)
            a = obj.data.decode("ascii")
            b = str(a)
            print("the code is:", a)
            request.session['id1'] = b
            i = i + 1
            return render(request, 'notify1_bb.html', {'param': b})
        cv2.imshow("qrcode", frame)
        cv2.waitKey(100)
        cv2.destroyAllWindows()
    return redirect('/get_i_s_bb')


def get_i_s_bb(request):
    if request.method == 'POST':
        emp_id = request.POST.get("a_id", "")
        request.session['id2'] = emp_id
        accession_no = request.POST.get("accession_no", "")
        if accession_no == '':
            print("yse")
            accession_no = request.session['id1']

        request.session['id1'] = accession_no
        print("done")

        return redirect('/issue_books_s_bb')

    return render(request, 'notify1_bb.html')


def issue_books_s_bb(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':

        accession_id = request.session['id1']

        student_id = request.session['id2']
        issue = request.POST.get("issue_date", "")

        issue_date = datetime.datetime.strptime(issue, '%Y-%m-%d')

        #due_day = request.POST.get("due_days", "")

        due_date =  request.POST.get("due_days", "")

        fine = 0
        ver1 = bookbank.objects.get(accession_number=accession_id)
        ver2 = students.objects.get(roll_no=student_id)
        try:

            sig = manage_bookbank(accession_id=accession_id, title=ver1.title, student_id=student_id,
                                  std_name=ver2.std_name, issue_date=issue_date, due_date=due_date, fine=fine)
            sig.save()
            print('done1')

            ver1 = students.objects.get(admission_no=student_id)
            no_books = ver1.no_books
            ver1.no_books = no_books + 1
            ver1.save()
            print('done2')
            ver2 = bookbank.objects.get(accession_number=accession_id)
            copy1 = ver2.copies
            ver2.copies = copy1 - 1
            ver2.save()
            print('done3')
            messages.info(request, "Book Issued Successfully")
            return render(request, 'notify1_bb.html')
        except:
            print('done4')
            return render(request, 'notify1_bb.html')
    else:
        try:
            accession_id = request.session['id1']
            try:
                ver3 = manage_bookbank.objects.get(accession_id=accession_id)
                print("pass1")
                if ver3.issued == 'yes':
                    print("pass2")
                    messages.info(request, "Alraedy Issued Book")
                    return render(request, 'issue_book_s_bb.html')
            except:
                pass
            print("pass4")
            ver1 = bookbank.objects.get(accession_number=accession_id)

            if ver1.copies == 0:
                messages.info(request, "Book is not Available")
                return render(request, 'issue_book_s_bb.html')
            elif ver1.withdrawal_no != '':
                messages.info(request, "Book is not Available")
                return render(request, 'issue_book_s_bb.html')

            student_id = request.session['id2']

            ver2 = students.objects.get(roll_no=student_id)
            if ver2.deleted == 'deleted':
                messages.info(request, "Can't Issue Book")
                return render(request, 'issue_book_s_bb.html')

            param = {"id": student_id, "name": ver2.std_name, "fname": ver2.fname, "gender": ver2.gender,
                     "contact_no": ver2.contact, "left": "No", "a_id": accession_id, "title": ver1.title,
                     "yop": ver1.yearPublication, "nop": ver1.no_pages, "cob": ver1.cost, "edition": ver1.edition,
                     "no_book": ver2.no_books}
            print(param)

            return render(request, 'issue_book_s_bb.html', param)
        except:
            messages.info(request, "No such record")
            return render(request, 'issue_book_s_bb.html')


def click_r_s_bb(request):
    i = 0
    cap = cv2.VideoCapture(0)
    while i < 1:
        _, frame = cap.read()
        decoded = pyzbar.decode(frame)
        for obj in decoded:
            print(obj)
            a = obj.data.decode("ascii")
            b = str(a)
            print("the code is:", a)
            request.session['id1'] = b
            i = i + 1
            return render(request, 'notify2_bb.html', {'param': b})
        cv2.imshow("qrcode", frame)
        cv2.waitKey(100)
        cv2.destroyAllWindows()
    return redirect('/get_r_s_bb')


def get_r_s_bb(request):
    if request.method == 'POST':
        accession_no = request.POST.get("a_id", "")
        if accession_no == '':
            print("yse")
            accession_no = request.session['id1']

        request.session['id1'] = accession_no
        print("done")
        return redirect('/return_books_s_bb')

    return render(request, 'notify2_bb.html')


def return_books_s_bb(request):
    if request.method == 'POST':
        return_dates = request.POST.get("return_date", "")
        print(return_dates)
        return_date = datetime.datetime.strptime(return_dates, '%Y-%m-%d').date()


        try:
            accession_id = request.session['id1']

            ver3 = manage_bookbank.objects.all().order_by('issue_date').reverse()
            for i in ver3:
                if i.accession_id == accession_id:
                    i.return_date = return_date
                    i.returned = "yes"
                    i.issued = "no"
                    i.fine = 0
                    i.save()
                    ver1 = students.objects.get(roll_no=i.student_id)
                    no_books = ver1.no_books
                    ver1.no_books = no_books - 1
                    ver1.save()
                    ver2 = bookbank.objects.get(accession_number=accession_id)
                    copy1 = ver2.copies
                    ver2.copies = copy1 + 1
                    ver2.save()
            messages.info(request, "Book Returned Successfully")
            return render(request, 'notify1_bb.html')
        except:
            messages.info(request, "Book Returned Successfully")
            return render(request, 'notify1_bb.html')

    try:
        accession_id = request.session['id1']
        print(accession_id)
        # emp_id = request.session['id2']
        print("d")
        ver3 = manage_bookbank.objects.all().order_by('issue_date').reverse()
        print("d1")
        for i in ver3:
            print("d2", i)
            if i.accession_id == accession_id:
                print("d3")
                if i.returned == 'yes':
                    print("d4")
                    messages.info(request, "Already Returned Book")
                    return render(request, 'return_book_s_bb.html')
                print("d5")
                ver2 = students.objects.get(roll_no=i.student_id)
                print("d6")
                ver1 = bookbank.objects.get(accession_number=accession_id)
                param = {"id": ver2.roll_no, "name": ver2.std_name, "fname": ver2.fname, "gender": ver2.gender,
                         "contact_no": ver2.contact, "left": "No", "a_id": accession_id, "title": ver1.title,
                         "yop": ver1.yearPublication, "nop": ver1.no_pages, "cob": ver1.cost, "edition": ver1.edition,
                         "fine": i.fine, "i_date": i.issue_date, "r_date": i.due_date, "no_book": ver2.no_books}
                print(param)
                return render(request, 'return_book_s_bb.html', param)
        print("d8")
        messages.info(request, "No such record")
        return render(request, 'return_book_s_bb.html')

    except:
        messages.info(request, "No such record")
        return render(request, 'return_book_s_bb.html')


def accession_register_bb(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        start_date = request.POST.get("dates", "")
        end_date = request.POST.get("dates1", "")
        title = request.POST.get("title", "")
        category = request.POST.get("category", "")
        deleted = request.POST.get("deleted", "")
        title_wise = request.POST.get("title_wise", "")
        category_wise = request.POST.get("category_wise", "")
        withdrawal = request.POST.get("withdrawal", "")

        try:
            if title_wise != '' and start_date == '' and end_date == '' and deleted == '' and withdrawal == '' and category == '' and title == '':

                obj = bookbank.objects.all().values('title', 'author', 'publisher').annotate(dcount=Count('title'))
                print(obj)
                return render(request, 'report1.html', {'query_results': obj})
            elif category_wise != '' and start_date == '' and end_date == '' and deleted == '' and withdrawal == '' and category == '' and title == '':
                obj = bookbank.objects.all().values('category').annotate(dcount=Count('category'))
                print(obj)
                return render(request, 'report2.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and deleted != '' and withdrawal != '' and category != '' and title != '':
                print("done1")
                obj = bookbank.objects.all().filter(dates__range=(start_date, end_date)).filter(
                    title__icontains=title).filter(category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and deleted != '' and withdrawal != '' and category != '' and title == '':
                print('done2')
                obj = bookbank.objects.all().filter(dates__range=(start_date, end_date)).filter(
                    withdrawal_no='').filter(
                    category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and deleted != '' and withdrawal != '' and category == '' and title != '':
                print('done3')
                obj = bookbank.objects.all().filter(dates__range=(start_date, end_date)).filter(
                    withdrawal_no='').filter(
                    title__icontains=title)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and deleted != '' and withdrawal != '' and category == '' and title == '':
                print('done4')
                obj = bookbank.objects.all().filter(dates__range=(start_date, end_date)).filter(withdrawal_no='')
                return render(request, 'report.html', {'query_results': obj})


            elif start_date != '' and end_date != '' and deleted != '' and withdrawal == '' and category != '' and title != '':
                print('done5')
                obj = bookbank.objects.all().filter(dates__range=(start_date, end_date)).filter(
                    withdrawal_no='').filter(
                    title__icontains=title).filter(category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and deleted != '' and withdrawal == '' and category != '' and title == '':
                print('done6')
                obj = bookbank.objects.all().filter(dates__range=(start_date, end_date)).filter(
                    withdrawal_no='').filter(
                    category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and deleted != '' and withdrawal == '' and category == '' and title != '':
                print('done7')
                obj = bookbank.objects.all().filter(dates__range=(start_date, end_date)).filter(
                    withdrawal_no='').filter(
                    title__icontains=title)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and deleted != '' and withdrawal == '' and category == '' and title == '':
                print('done8')
                obj = bookbank.objects.all().filter(dates__range=(start_date, end_date)).filter(withdrawal_no='')
                return render(request, 'report.html', {'query_results': obj})


            elif start_date != '' and end_date != '' and withdrawal != '' and deleted == '' and category != '' and title != '':
                print('done9')
                obj = bookbank.objects.all().filter(dates__range=(start_date, end_date)).filter(deleted='').filter(
                    title__icontains=title).filter(category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and withdrawal != '' and deleted == '' and category != '' and title == '':
                print('done10')
                obj = bookbank.objects.all().filter(dates__range=(start_date, end_date)).filter(deleted='').filter(
                    category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and withdrawal != '' and deleted == '' and category == '' and title != '':
                print('done11')
                obj = bookbank.objects.all().filter(dates__range=(start_date, end_date)).filter(deleted='').filter(
                    title__icontains=title)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and withdrawal != '' and deleted == '' and category == '' and title == '':
                print('done12')
                obj = bookbank.objects.all().filter(dates__range=(start_date, end_date)).filter(deleted='')
                return render(request, 'report.html', {'query_results': obj})


            elif start_date == '' and end_date == '' and withdrawal != '' and deleted == '' and category != '' and title != '':
                print("done13")
                obj = bookbank.objects.all().filter(deleted='').filter(title__icontains=title).filter(
                    category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date == '' and end_date == '' and withdrawal != '' and deleted == '' and category != '' and title == '':
                print("done14")
                obj = bookbank.objects.all().filter(deleted='').filter(category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date == '' and end_date == '' and withdrawal != '' and deleted == '' and category == '' and title != '':
                print("done15")
                obj = bookbank.objects.all().filter(deleted='').filter(title__icontains=title)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date == '' and end_date == '' and withdrawal != '' and deleted == '' and category == '' and title == '':
                print("done16")
                obj = bookbank.objects.all().filter(deleted='')
                return render(request, 'report.html', {'query_results': obj})


            elif start_date == '' and end_date == '' and deleted != '' and withdrawal == '' and category != '' and title != '':
                print("done17")
                obj = bookbank.objects.all().filter(withdrawal_no='').filter(title__icontains=title).filter(
                    category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date == '' and end_date == '' and deleted != '' and withdrawal == '' and category != '' and title == '':
                print("done18")
                obj = bookbank.objects.all().filter(withdrawal_no='').filter(category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date == '' and end_date == '' and deleted != '' and withdrawal == '' and category == '' and title != '':
                print("done19")
                obj = bookbank.objects.all().filter(withdrawal_no='').filter(title__icontains=title)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date == '' and end_date == '' and deleted != '' and withdrawal == '' and category == '' and title == '':
                print("done20")
                obj = bookbank.objects.all().filter(withdrawal_no='')
                return render(request, 'report.html', {'query_results': obj})



            elif start_date == '' and end_date == '' and withdrawal != '' and deleted != '' and category != '' and title != '':
                print('done21')
                obj = bookbank.objects.all().filter(title__icontains=title).filter(category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date == '' and end_date == '' and withdrawal != '' and deleted != '' and category != '' and title == '':
                print('d22')
                obj = bookbank.objects.all().filter(category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date == '' and end_date == '' and withdrawal != '' and deleted != '' and category == '' and title != '':
                print('dw23')
                obj = bookbank.objects.all().filter(title__icontains=title)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date == '' and end_date == '' and withdrawal != '' and deleted != '' and category == '' and title == '':
                print('dw24')
                obj = bookbank.objects.all()
                return render(request, 'report.html', {'query_results': obj})



            elif start_date != '' and end_date != '' and deleted == '' and withdrawal == '' and category != '' and title != '':
                print("done25")
                obj = bookbank.objects.all().filter(dates__range=(start_date, end_date)).filter(
                    withdrawal_no='').filter(
                    deleted='').filter(title__icontains=title).filter(category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and deleted == '' and withdrawal == '' and category != '' and title == '':
                print("done26")
                obj = bookbank.objects.all().filter(dates__range=(start_date, end_date)).filter(
                    withdrawal_no='').filter(
                    deleted='').filter(category__icontains=category)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and deleted == '' and withdrawal == '' and category == '' and title != '':
                print("done27")
                obj = bookbank.objects.all().filter(dates__range=(start_date, end_date)).filter(
                    withdrawal_no='').filter(
                    deleted='').filter(title__icontains=title)
                return render(request, 'report.html', {'query_results': obj})
            elif start_date != '' and end_date != '' and deleted == '' and withdrawal == '' and category == '' and title == '':
                print("done28")
                obj = bookbank.objects.all().filter(dates__range=(start_date, end_date)).filter(
                    withdrawal_no='').filter(
                    deleted='')
                return render(request, 'report.html', {'query_results': obj})



            elif category != '' and start_date == '' and end_date == '' and deleted == '' and withdrawal == '' and title == '':
                print("done29")
                obj = bookbank.objects.all().filter(category__icontains=category).filter(withdrawal_no='').filter(
                    deleted='')
                return render(request, 'report.html', {'query_results': obj})
            elif title != '' and start_date == '' and end_date == '' and deleted == '' and withdrawal == '' and category == '':
                print("done30")
                obj = bookbank.objects.all().filter(title__icontains=title).filter(withdrawal_no='').filter(deleted='')
                return render(request, 'report.html', {'query_results': obj})
            elif title != '' and start_date == '' and end_date == '' and deleted == '' and withdrawal == '' and category != '':
                print("done31")
                obj = bookbank.objects.all().filter(title__icontains=title).filter(category__icontains=category).filter(
                    withdrawal_no='').filter(deleted='')
                return render(request, 'report.html', {'query_results': obj})


            elif start_date == '' and end_date == '' and deleted == '' and withdrawal == '' and category == '' and title == '':
                print("done32")
                obj = bookbank.objects.all().filter(withdrawal_no='').filter(deleted='')
                return render(request, 'report.html', {'query_results': obj})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in list")
            return render(request, 'list_bb.html')
    else:
        return render(request, 'list_bb.html')


def issue_register_bb(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        date1 = request.POST.get("date", "")
        month = request.POST.get("month", "")
        title = request.POST.get("title", "")
        year = request.POST.get("year", "")

        try:
            if date1 != '' and month != '' and year != '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                           issue_date__month=month,
                                                                                           issue_date__day=date1).order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    title__icontains=title).order_by('issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year).filter(
                    title__icontains=title).order_by('issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).order_by('issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year != '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year, issue_date__month=month,
                                                            issue_date__day=date1).order_by('issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__month=month, issue_date__day=date1).order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__day=date1).order_by('issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(
                    issue_date__year=year, issue_date__day=date1).order_by('issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(
                    issue_date__day=date1).order_by('issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month, issue_date__day=date1).order_by('issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month).order_by('issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                           date_of_receipt__day=date1)
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year).order_by('issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__month=month).order_by('issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year, issue_date__day=date1).order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year, issue_date__month=month).order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '':
                ver3 = manage_bookbank.objects.all().order_by('issue_date').reverse()
                return render(request, 'issue_return.html', {'query_results': ver3})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in list")
            return render(request, 'list1_bb.html')
    else:
        ver3 = manage_bookbank.objects.all().order_by('issue_date').reverse()
        return render(request, 'issue_return.html', {'query_results': ver3})


def withdraw_register_bb(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        date1 = request.POST.get("date", "")
        month = request.POST.get("month", "")
        title = request.POST.get("title", "")
        year = request.POST.get("year", "")

        try:
            if date1 != '' and month != '' and year != '' and title != '':
                ver3 = bookbank.objects.all().filter(title__icontains=title).filter(withdrawal_date__year=year,
                                                                                    withdrawal_date__month=month,
                                                                                    withdrawal_date__day=date1).filter(
                    ~Q(withdrawal_no='')).order_by('withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title != '':
                ver3 = bookbank.objects.all().filter(withdrawal_date__year=year, withdrawal_date__month=month).filter(
                    title__icontains=title).filter(~Q(withdrawal_no='')).order_by('withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = bookbank.objects.all().filter(withdrawal_date__year=year).filter(
                    title__icontains=title).filter(~Q(withdrawal_no='')).order_by('withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title != '':
                ver3 = bookbank.objects.all().filter(title__icontains=title).filter(~Q(withdrawal_no='')).order_by(
                    'withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year != '' and title == '':
                ver3 = bookbank.objects.all().filter(withdrawal_date__year=year, withdrawal_date__month=month,
                                                     withdrawal_date__day=date1).filter(~Q(withdrawal_no='')).order_by(
                    'withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title == '':
                ver3 = bookbank.objects.all().filter(withdrawal_date__month=month, withdrawal_date__day=date1).filter(
                    ~Q(withdrawal_no='')).order_by('withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title == '':
                ver3 = bookbank.objects.all().filter(withdrawal_date__day=date1).filter(~Q(withdrawal_no='')).order_by(
                    'withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title != '':
                ver3 = bookbank.objects.all().filter(title__icontains=title).filter(
                    withdrawal_date__year=year, withdrawal_date__day=date1).filter(~Q(withdrawal_no='')).order_by(
                    'withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title != '':
                ver3 = bookbank.objects.all().filter(title__icontains=title).filter(
                    withdrawal_date__day=date1).filter(~Q(withdrawal_no='')).order_by('withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title != '':
                ver3 = bookbank.objects.all().filter(title__icontains=title).filter(
                    withdrawal_date__month=month, withdrawal_date__day=date1).filter(~Q(withdrawal_no='')).order_by(
                    'withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title != '':
                ver3 = bookbank.objects.all().filter(title__icontains=title).filter(
                    withdrawal_date__month=month).filter(~Q(withdrawal_no='')).order_by('withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = bookbank.objects.all().filter(title__icontains=title).filter(withdrawal_date__year=year,
                                                                                    date_of_receipt__day=date1).filter(
                    ~Q(withdrawal_no='')).order_by('withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title == '':
                ver3 = bookbank.objects.all().filter(withdrawal_date__year=year).filter(~Q(withdrawal_no='')).order_by(
                    'withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title == '':
                ver3 = bookbank.objects.all().filter(withdrawal_date__month=month).filter(
                    ~Q(withdrawal_no='')).order_by('withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title == '':
                ver3 = bookbank.objects.all().filter(withdrawal_date__year=year, withdrawal_date__day=date1).filter(
                    ~Q(withdrawal_no='')).order_by('withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title == '':
                ver3 = bookbank.objects.all().filter(withdrawal_date__year=year, withdrawal_date__month=month).filter(
                    ~Q(withdrawal_no='')).order_by('withdrawal_date').reverse()
                return render(request, 'report.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '':
                ver3 = bookbank.objects.all().order_by('withdrawal_date').reverse().filter(~Q(withdrawal_no=''))
                return render(request, 'report.html', {'query_results': ver3})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in list")
            return render(request, 'list5_bb.html')
    else:
        return render(request, 'list5_bb.html')


def return_register_bb(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        date1 = request.POST.get("date", "")
        month = request.POST.get("month", "")
        title = request.POST.get("title", "")
        year = request.POST.get("year", "")

        try:
            if date1 != '' and month != '' and year != '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                           issue_date__month=month,
                                                                                           issue_date__day=date1).filter(
                    returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    title__icontains=title).filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year).filter(
                    title__icontains=title).filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year != '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year, issue_date__month=month,
                                                            issue_date__day=date1).filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__month=month, issue_date__day=date1).filter(
                    returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__day=date1).filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(
                    issue_date__year=year, issue_date__day=date1).filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(
                    issue_date__day=date1).filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month, issue_date__day=date1).filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month).filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                           date_of_receipt__day=date1).filter(
                    returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year).filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__month=month).filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year, issue_date__day=date1).filter(
                    returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '':
                ver3 = manage_bookbank.objects.all().order_by('issue_date').reverse().filter(returned='yes')
                return render(request, 'issue_return.html', {'query_results': ver3})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in list")
            return render(request, 'list2_bb.html')
    else:
        return render(request, 'list2_bb.html')


def over_due_bb(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        date1 = request.POST.get("date", "")
        month = request.POST.get("month", "")
        title = request.POST.get("title", "")
        year = request.POST.get("year", "")

        try:
            if date1 != '' and month != '' and year != '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                           issue_date__month=month,
                                                                                           issue_date__day=date1).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse()
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    title__icontains=title).filter(due_date__lt=datetime.date.today()).filter(returned='no').order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year).filter(
                    title__icontains=title).filter(due_date__lt=datetime.date.today()).filter(returned='no').order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse()
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year != '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year, issue_date__month=month,
                                                            issue_date__day=date1).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse()
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__month=month, issue_date__day=date1).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse()
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__day=date1).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse()
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(
                    issue_date__year=year, issue_date__day=date1).filter(due_date__lt=datetime.date.today()).filter(
                    returned='no').order_by('issue_date').reverse()
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(
                    issue_date__day=date1).filter(due_date__lt=datetime.date.today()).filter(returned='no').order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month, issue_date__day=date1).filter(due_date__lt=datetime.date.today()).filter(
                    returned='no').order_by('issue_date').reverse()
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month).filter(due_date__lt=datetime.date.today()).filter(returned='no').order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                           date_of_receipt__day=date1).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse()
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse()
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__month=month).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse()
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year, issue_date__day=date1).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse()
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    due_date__lt=datetime.date.today()).filter(returned='no').order_by('issue_date').reverse()
                return render(request, 'issue_return2.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '':
                ver3 = manage_bookbank.objects.all().order_by('issue_date').reverse().filter(
                    due_date__lt=datetime.date.today()).filter(returned='no')
                return render(request, 'issue_return2.html', {'query_results': ver3})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in list")
            return render(request, 'list3_bb.html')
    else:
        ver3 = manage_bookbank.objects.all().order_by('issue_date').reverse().filter(
            due_date__lt=datetime.date.today()).filter(returned='no')
        return render(request, 'issue_return2.html', {'query_results': ver3})


def pending_bb(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        date1 = request.POST.get("date", "")
        month = request.POST.get("month", "")
        title = request.POST.get("title", "")
        year = request.POST.get("year", "")
        accession_id = request.POST.get("accession_id", "")

        try:
            if date1 != '' and month != '' and year != '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                           issue_date__month=month,
                                                                                           issue_date__day=date1).filter(
                    returned='no').order_by('issue_date').reverse()
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    title__icontains=title).filter(returned='no').order_by('issue_date').reverse()
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year).filter(
                    title__icontains=title).filter(returned='no').order_by('issue_date').reverse()
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(returned='no').order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year != '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year, issue_date__month=month,
                                                            issue_date__day=date1).filter(returned='no').order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__month=month, issue_date__day=date1).filter(
                    returned='no').order_by('issue_date').reverse()
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__day=date1).filter(returned='no').order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(
                    issue_date__year=year, issue_date__day=date1).filter(returned='no').order_by('issue_date').reverse()
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year == '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(
                    issue_date__day=date1).filter(returned='no').order_by('issue_date').reverse()
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 != '' and month != '' and year == '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month, issue_date__day=date1).filter(returned='no').order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(
                    issue_date__month=month).filter(returned='no').order_by('issue_date').reverse()
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title != '':
                ver3 = manage_bookbank.objects.all().filter(title__icontains=title).filter(issue_date__year=year,
                                                                                           date_of_receipt__day=date1).filter(
                    returned='no').order_by('issue_date').reverse()
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year != '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year).filter(returned='no').order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year == '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__month=month).filter(returned='no').order_by(
                    'issue_date').reverse()
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 != '' and month == '' and year != '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year, issue_date__day=date1).filter(
                    returned='no').order_by('issue_date').reverse()
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month != '' and year != '' and title == '':
                ver3 = manage_bookbank.objects.all().filter(issue_date__year=year, issue_date__month=month).filter(
                    returned='no').order_by('issue_date').reverse()
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '' and accession_id!='':
                ver3 = manage_bookbank.objects.all().order_by('issue_date').reverse().filter(accession_id=accession_id).filter(returned='no')
                return render(request, 'issue_return3.html', {'query_results': ver3})
            elif date1 == '' and month == '' and year == '' and title == '':
                ver3 = manage_bookbank.objects.all().order_by('issue_date').reverse().filter(returned='no')
                return render(request, 'issue_return3.html', {'query_results': ver3})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in list")
            return render(request, 'list4_bb.html')
    else:
        '''ver3 = manage_bookbank.objects.all().order_by('issue_date').reverse().filter(returned='no')
        return render(request, 'issue_return3.html', {'query_results': ver3})'''
        return render(request, 'list4_bb.html')

def click_w_rb(request):
    i = 0
    cap = cv2.VideoCapture(0)
    while i < 1:
        _, frame = cap.read()
        decoded = pyzbar.decode(frame)
        for obj in decoded:
            print(obj)
            a = obj.data.decode("ascii")
            b = str(a)
            print("the code is:", a)
            request.session['id1'] = b
            i = i + 1
            return render(request, 'write_in_bb.html', {'param': b})
        cv2.imshow("qrcode", frame)
        cv2.waitKey(100)
        cv2.destroyAllWindows()
    return redirect('/write_in_bookbank')


def get_d_w_rb(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        accession_no = request.POST.get("accession_no", "")

        try:
            if accession_no == '':
                accession_no = request.session['id1']
            request.session['id1'] = accession_no

            ver = bookbank.objects.get(accession_number=accession_no)
            if ver.withdrawal_no == "":
                messages.error(request, "Already Write in")
                return render(request, 'write_in_wb.html')
            else:

                return render(request, 'write_in_wb.html',
                              {'accession_number': ver.accession_number, "title": ver.title, "author": ver.author,
                               "classification": ver.classification, "publisher": ver.publisher,
                               "category": ver.category,
                               "yearPublication": ver.yearPublication, "no_pages": ver.no_pages, "cost": ver.cost,
                               "edition": ver.edition, "volume": ver.volume})

        except:
            messages.error(request, "There are some Errors!!Please try again")
            return render(request, 'write_in_wb.html')
    return render(request, 'write_in_bb.html')


def write_in_bookbank(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        accession_no = request.POST.get("accession_no", "")

        try:
            if accession_no == '':
                accession_no = request.session['id1']
            ver = bookbank.objects.get(accession_number=accession_no)
            ver.withdrawal_no = ''
            ver.withdrawal_date = None
            ver.save()
            messages.error(request, "Book Write In Successfully")

            return render(request, 'write_in_bb.html')
        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in delete")
            return render(request, 'write_in_bb.html')
    else:
        return render(request, 'write_in_bb.html', )


def std_emp_search(request):
    if not request.user.is_authenticated:
        return redirect("/")
    if request.method == 'POST':
        roll_no = request.POST.get("roll_no", "")
        emp_id = request.POST.get("emp_id", "")

        try:
            if roll_no != '' and emp_id == '':
                ver3 = manage_books.objects.all().filter(student_id=roll_no)
                ver4 = manage_bookbank.objects.all().filter(student_id=roll_no)
                ver2 = students.objects.get(roll_no=roll_no)
                param = {"id": ver2.roll_no, "name": ver2.std_name, "fname": ver2.fname, "mname": ver2.mname,
                         "dob": ver2.dob, "gender": ver2.gender,
                         "contact": ver2.contact, "query_results": ver3, "query_results1": ver4}
                print(param)

                return render(request, 'search_report.html', param)

            elif emp_id != '' and roll_no == '':
                ver3 = manage_books.objects.all().filter(emp_id=emp_id)
                ver4 = manage_bookbank.objects.all().filter(emp_id=emp_id)
                ver2 = employees.objects.get(emp_id=emp_id)
                param = {"id": ver2.emp_id, "name": ver2.emp_name, "fname": ver2.fname, "sname": ver2.spouse_name,
                         "dob": ver2.dob, "gender": ver2.gender,
                         "contact": ver2.contact, "query_results": ver3, "query_results1": ver4}
                print(param)

                return render(request, 'search_report1.html', param)

            elif emp_id != '' and roll_no != '':
                messages.error(request, "Select Only One Field")
                print("2 fields")
                return render(request, 'search_s_e.html')


        except:
            messages.error(request, "There are some Errors!!Please try again")
            print("error in search")
            return render(request, 'search_s_e.html')
    else:
        return render(request, 'search_s_e.html', )


