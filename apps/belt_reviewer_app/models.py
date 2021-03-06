from __future__ import unicode_literals
from django.db import models
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re

# This class handles all of the validation for our registration form on submit
class UserManager(models.Manager):
    def basic_validator(self, postData):
        errors = {}
        #validate length of first name field
        if len(postData['input_first_name']) < 2:
            errors["input_first_name_length"] = "First name should be at least 2 letters"
        #validate first name field doesn't contain numbers
        if postData['input_first_name'].isalpha() == False:
            errors["input_first_name_alpha"] = "First name cannot contain numbers"
        #validate length of last name field
        if len(postData['input_last_name']) < 2:
            errors["input_last_name_length"] = "Last name should be at least 2 letters"
        #validate last name field doesn't contain numbers
        if postData['input_last_name'].isalpha() == False:
            errors["input_last_name_alpha"] = "Last name cannot contain numbers"
        # query the list of all emails to verify the desired address is not registered yet
        query = User.objects.all().values('email')
        for row in query:
            for key in row:
                if row[key] == postData['input_email']:
                    errors["input_email"] = "Email is taken"
        # validate that the email supplied by the user is of a valid format
        try:
            validate_email(postData["input_email"])
        except ValidationError:
            errors['input_email'] = "Enter a valid email"
        # validates password is longer than 8
        if len(postData['input_password']) < 8:
            errors["input_password"] = "Password should be at least 8 characters"
        # Validates that the confirm_password field matches the password field
        if postData['input_confirm_password'] != postData["input_password"]:
            errors["input_confirm_password"] = "Passwords must match"
        return errors

# This is our User table for registration and login
class User(models.Model):
    first_name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    objects = UserManager()
    def __repr__(self):
        return "<User object: {} {} {}>".format(self.first_name, self.last_name, self.email)

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    objects = UserManager()
    def __repr__(self):
        return "<Book object: {} {}>".format(self.title, self.author)

class Review(models.Model):
    review = models.TextField()
    rating = models.IntegerField()
    reviewed_books = models.ForeignKey(Book, related_name="book_reviews")
    reviewed_users = models.ForeignKey(User, related_name="user_reviews")
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    objects = UserManager()
    def __repr__(self):
        return "<Review object: {} {} {}>".format(self.review, self.reviewed_books, self.reviewed_users)