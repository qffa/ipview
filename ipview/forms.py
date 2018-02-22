from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, ValidationError, TextAreaField, IntegerField
from wtforms.validators import Length, Email, EqualTo, Required, NumberRange
from ipview.models import db, Site, Subnet, User



class LoginForm(FlaskForm):
    username = StringField(
            "Username", 
            render_kw={
                "placeholder": "Username",
                "class": "form-control",
                "required":'',
                "autofocus": ''
                },
            validators=[Required()]
            )

    password = PasswordField(
            "Password", 
            render_kw={
                "placeholder": "Password",
                "class": "form-control",
                "required":''
                },
            validators=[Required()]
            )

    submit = SubmitField(
            "Sign in",
            render_kw={"class": "btn btn-lg btn-primary btn-block"}
            )



    def validate_username(self, field):
        if field.data and not User.query.filter_by(username=field.data).first():
            flash("User does not exist.", "danger")
            raise ValidationError("user does not exist")


    def validate_password(self, field):
        user = User.query.filter_by(username=self.username.data).first()
        if user and not user.check_password(field.data):
            flash("Wrong password", "danger")
            raise ValidationError("wrong password")




class SiteForm(FlaskForm):
    site_name = StringField(
            "Site Name",
            validators=[Required(), Length(4, 30)]
            )
    description = TextAreaField(
            "Description",
            validators=[Required(), Length(4, 200)]
            )
    submit = SubmitField("Submit")


'''
    def validate_site_name(self, field):
        if Site.query.filter_by(site_name=field.data).first():
            raise ValidationError("Site exists")
'''


class AddSubnetForm(FlaskForm):
    subnet_name = StringField(
        "Subnet Name",
        validators=[Required(),
        Length(4, 30)]
        )
    subnet_address = StringField(
        "Subnet Address",
        render_kw={"placeholder": "192.168.1.0/24"},
        validators=[Required(), Length(4, 60)]
        )
    gateway = StringField(
        "Gateway",
        validators=[Length(0, 60),]
        )
    dns = StringField(
        "DNS",
        validators=[Length(0, 200)]
        )
    site_id = SelectField(
        "Site", 
        coerce=int,
        validators=[Required()]
        )
    description = StringField(
        "Description",
        validators=[Length(4, 200)]
        )
    vlan = IntegerField(
        "VLAN ID",
        description="* 0 means not a VLAN",
        validators=[NumberRange(0, 4096)]
        )
    submit = SubmitField("Submit")




class FilterForm(FlaskForm):
    filter_by = SelectField(
        "filter",
        validators=[Required()]
        )
    value = StringField(
        "value",
        validators=[Required(), Length(2, 64)]
        )
    submit = SubmitField("Submit")



