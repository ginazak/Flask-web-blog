from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length
from wtforms import PasswordField, SubmitField, SelectField
from wtforms.validators import Email, EqualTo, ValidationError,Regexp, InputRequired 
from blog.models import User
from flask import request


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),Length(min=3, max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Regexp('^.{6,8}$', message='Your password should be between 6 and 8 characters long')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Email is invalid')
    def validate_password(self, password):
        user = User.query.filter_by(password=password.data).first()
        if user:
            raise ValidationError('Password is invalid')

class ContactForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    name = StringField('Name', validators=[DataRequired()])
    message = StringField('Message', validators=[DataRequired()])
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    comment = StringField('Comment', validators=[InputRequired()])
    submit = SubmitField('Post comment')



# Code to build tagging system adapted from 
# Learning Flask Framework e-book by OReilly
# accessed 21-2-2021 
# from https://learning.oreilly.com/library/view/learning-flask-framework/9781783983360/ch04s03.html
class TagField(StringField):
    def _value(self):
        if self.data:
            return ', '.join([tag.name for tag in self.data])
        return ''

    def get_tags_from_string(self, tag_string):
        raw_tags = tag_string.split(',')
        tag_names = [name.strip() for name in raw_tags if name.strip()]
        existing_tags = Tag.query.filter(Tag.name.in_(tag_names))
        new_names = set(tag_names) - set([tag.name for tag in existing_tags])
        new_tags = [Tag(name=name) for name in new_names]
        return list(existing_tags) + new_tags

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = self.get_tags_from_string(valuelist[0])
        else:
            self.data = []


class TagForm(FlaskForm):
    tags = TagField(
        'Tags',
        description='Separate multiple tags with commas.')
    submit = SubmitField('tag field')

    def save_tag(self, tag):
        self.populate_obj(tag)
        tag.generate_slug()
        return tag
