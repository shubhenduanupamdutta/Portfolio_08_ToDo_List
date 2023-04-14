from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, EmailField, DateField
from wtforms.validators import InputRequired, NumberRange, Email, Length, EqualTo


# Creating form to add a task
class NewTask(FlaskForm):
    task = StringField(validators=[InputRequired(), Length(min=1, max=250)])
    estimated_end_date = DateField(label="Deadline")
    submit = SubmitField(label="Add Task", render_kw={"class": "w-25 btn btn-primary"})


# Creating a register form
class RegisterForm(FlaskForm):
    name = StringField(label="Name", validators=[InputRequired(), Length(min=1, max=250)])
    email = EmailField(label="Email", validators=[InputRequired(), Length(min=1, max=250), Email()])
    password = PasswordField(label="Password", validators=[InputRequired(), Length(min=8, max=100)])
    confirm_password = PasswordField(label="Confirm Password",
                                   validators=[InputRequired(), EqualTo('password', message="Passwords Don't Match")])
    submit = SubmitField(label="Sign Me Up!")


# Creating a login form
class LoginForm(FlaskForm):
    email = EmailField(label="Email", validators=[InputRequired(), Length(min=1, max=250), Email()])
    password = PasswordField(label="Password", validators=[InputRequired(), Length(min=8, max=100)])
    submit = SubmitField(label="Log Me In!")
