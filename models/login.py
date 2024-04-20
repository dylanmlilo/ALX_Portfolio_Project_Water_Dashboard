from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError


class LoginForm(FlaskForm):
    """
    Represents a login form with fields for username, password, and a submit button.

    Attributes:
        username (StringField): Field for entering the username with length validation and placeholder text.
        password (PasswordField): Field for entering the password with length validation and placeholder text.
        submit (SubmitField): Button to submit the login form.
    """
    username = StringField(validators=[
        InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
        InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')
    
