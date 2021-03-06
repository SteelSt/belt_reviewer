#import needed django modules
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib import messages
from django.contrib import auth
from django.db import connection

#import bcrypt
import bcrypt

#  import our db(s)
from .models import *

#This is our index page and contains login and registration forms
def loginandreg(request):
    return render(request,'belt_reviewer_app/loginandreg.html')

#Processes information from the registration form
def process_register(request, methods=['POST']):
    # pass the post data to the method we wrote and save the response in a variable called errors
    errors = User.objects.basic_validator(request.POST)
    # check if the errors object has anything in it
    if len(errors):
        # if the errors object contains anything, loop through each key-value pair and make a flash message
        for key, value in errors.items():
            messages.error(request, value)
            print("WEVE HIT AN ERROR")
        # redirect the user back to the form to fix the errors
        return redirect('/', id)
    else:
        # if the errors object is empty, that means there were no errors!
        # add our new record to the table , push what we need to session,
        # and redirect to /success to render our final page
        User.objects.create(first_name=request.POST['input_first_name'], last_name=request.POST['input_last_name'], email=request.POST['input_email'], password=bcrypt.hashpw(request.POST['input_password'].encode('utf8'), bcrypt.gensalt()))
        query = User.objects.filter(email=request.POST['input_email']).values('id', 'email')
        for row in query:
            request.session['isloggedin'] = row['id']
            request.session['useremail'] = row['email']
        request.session['error'] = ""
        request.session['welcomename'] = request.POST['input_first_name']
        request.session['welcomemessage'] = 'Successfully registered!'
        return redirect('/books')

#Processes information from the login form
def process_login(request, methods=['POST']):
    # Query the data we need
    query = User.objects.all().values('id', 'email', 'first_name', 'password')
    # Iterate through query until we find user email then verify password is legit
    for row in query:
        if row['email'] == request.POST['login_email'] and bcrypt.checkpw(request.POST['login_password'].encode(), row['password'].encode()): 
            request.session['error'] = ""
            request.session['useremail'] = row['email']
            request.session['isloggedin'] =  row['id']
            request.session['welcomename'] = row['first_name']
            request.session['welcomemessage'] = 'Successfully logged in!'
            return redirect('/books')
    request.session['error'] = "• Try again"
    return redirect('/')

#This is the landing page that the user arrives at after registering or logging in
def books(request):
    # If the user has a isLoggedin session
    query = User.objects.filter(id=request.session['isloggedin']).values('id', 'email')
    if 'isloggedin' in request.session:
        for row in query:
            if request.session['isloggedin'] == row['id'] and request.session['useremail'] == row['email']:
                context ={
                    "recent_reviews" : Review.objects.order_by("-id")[:3],
                    "books_with_reviews" : Book.objects.order_by("-id")[3:]
                }
                return render(request,'belt_reviewer_app/books.html', context)
    else:
        return redirect('/')

def addbook(request):
    return render(request, 'belt_reviewer_app/addbook.html')

def processbook(request, methods=['POST']):
    if request.POST['addauthor'] == "":
        author = request.POST['authorlist']
    else:
        author = request.POST['addauthor']
    this_user = User.objects.get(id=request.session['isloggedin'])
    Book.objects.create(title=request.POST['title'], author=author)
    this_book = Book.objects.last()
    Review.objects.create(review=request.POST['review'], reviewed_books=this_book, reviewed_users=this_user, rating=request.POST['rating'])
    return redirect('/books')

def process_review(request, methods=['POST']):
    this_book = Book.objects.get(id=request.POST['book_id'])
    this_user = User.objects.get(id=request.session['isloggedin'])
    Review.objects.create(review=request.POST['review'], reviewed_books=this_book, reviewed_users=this_user, rating=request.POST['rating'])
    return redirect('/books/{}'.format(request.POST['book_id']))

def showbook(request, num):
    context={
        "the_book": Book.objects.get(id=num),
        "all_reviews": Review.objects.filter(reviewed_books=num).order_by("-created_at")
    }
    return render(request,'belt_reviewer_app/showbook.html', context)

def delete(request, num):
    the_review = Review.objects.get(id=num)
    the_book = the_review.reviewed_books.id
    the_review.delete()
    return redirect('/books/{}'.format(the_book))

def users(request, num):
    context={
        "user_data": User.objects.get(id=request.session['isloggedin']),
        "post_count": User.objects.get(id=request.session['isloggedin']).user_reviews.count(),
        "reviewed_things": User.objects.get(id=request.session['isloggedin']).user_reviews.all(),
    }
    reviewed_things = User.objects.get(id=request.session['isloggedin']).user_reviews.all()
    print("REVIEWED THINGS: ", reviewed_things)
    return render(request, 'belt_reviewer_app/users.html', context)

# Clears out session / logs out the user
def logout(request):
    auth.logout(request)
    return redirect('/')