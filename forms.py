from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, ValidationError


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),Length(min=4, max=200)])
    email = EmailField('Email', validators=[DataRequired(),Length(min=4, max=300) ,Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8,max=300)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),Length(min=8,max=300),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Register')
    def validate_confirm_password(self, field):
        if field.data != self.password.data:
            raise ValidationError('Passwords must match.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Length( max=200)])
    password = PasswordField('Password', validators=[DataRequired(),Length(min=8, max=300)])
    submit = SubmitField('Let Me In')


class AddDetailsForm(FlaskForm):
    gender = SelectField('Gender', choices=['Male','Female'],validators=[DataRequired()])
    weight_kg = StringField('Weight', validators=[DataRequired(),Regexp(r'^\d+([\.,]\d+)?$', message='Weight must be a valid number.')])
    height_cm = StringField('Height', validators=[DataRequired(),Regexp(r'^\d+([\.]\d+)?$', message='Height must be a valid number.')])

    submit = SubmitField('Submit')


class BmiCalcForm(FlaskForm):
    weight_kg = StringField('Weight (kg)', validators=[DataRequired(),Regexp(r'^\d+([\.,]\d+)?$', message='Weight must be a valid number.')])
    height_cm = StringField('Height (cm)', validators=[DataRequired(),Regexp(r'^\d+([\.]\d+)?$', message='Height must be a valid number.')])

    submit = SubmitField('Submit')


class CalorieByActivitiesForm(FlaskForm):
    query = StringField('Activity', validators=[DataRequired()])


class AddBirthdayForm(FlaskForm):
     # Birthday fields
    birth_day = SelectField('Day', choices=[(str(day), str(day)) for day in range(1, 32)], validators=[DataRequired()])
    birth_month = SelectField(
        'Month',
        choices=[
            ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'),
            ('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
        ],
        validators=[DataRequired()]
    )
    birth_year = SelectField('Year', choices=[(str(year), str(year)) for year in range(1900, 2023)], validators=[DataRequired()])

    submit = SubmitField('Submit')


class ChangeUsernameForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(),Length(min=4, max=200)])
    submit = SubmitField('Update Details')


class ResetPasswordForm(FlaskForm):
    old_password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=300)])
    new_password = PasswordField('Password', validators=[DataRequired(), Length(min=8,max=300)])
    new_confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),Length(min=8,max=300),
        EqualTo('new_password', message='Passwords must match.')
    ])

    submit = SubmitField('Reset Password')
    def validate_confirm_password(self, field):
        if field.data != self.new_password.data:
            raise ValidationError('Passwords must match.')
