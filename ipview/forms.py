import re
import ipaddress
from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, ValidationError, TextAreaField, IntegerField, HiddenField
from wtforms.validators import Length, Email, EqualTo, Required, NumberRange, MacAddress
from ipview.models import db, Site, Network, Subnet, User
from flask_login import current_user




"""
validation class
"""

class NameUniqueIn(object):
    def __init__(self, table, message=None):
        self.table = table
        if not message:
            message = "name conflict"
        self.message = message

    def __call__(self, form, field):
        if self.table.query.filter_by(name=field.data).first():
            raise ValidationError(self.message)

class IPAddress(object):
    def __init__(self, message=None):
        if not message:
            message = "wrong IP format"
        self.message = message

    def __call__(self, form, field):
        if field.data != '':
            try:
                ipaddress.ip_address(field.data)
            except:
                raise ValidationError(self.message)
        
class NetworkAddress(object):
    def __init__(self, message=None):
        if not message:
            message = "wrong subnet format"
        self.message = message

    def __call__(self, form, field):
        try:
            ipaddress.ip_network(field.data)
        except:
            raise ValidationError(self.message)



"""
form class
"""

class LoginForm(FlaskForm):
    username = StringField(
            "Username", 
            render_kw={
                "placeholder": "Username",
                "class": "form-control",
                "required":''
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



class ChangePasswordForm(FlaskForm):
    password = PasswordField(
        "Password",
        render_kw = {
            "autofocus": ''
        },
        validators = [Required()]
        )
    
    new_password = PasswordField(
        "New Password",
        validators = [Required(), Length(6, 24)]
        )

    repeat_password = PasswordField(
        "Repeat Password",
        validators = [Required(), EqualTo('new_password', "password not match")]
        )

    submit = SubmitField(
        "Submit"
        )

    def validate_password(self, field):
        if not current_user.check_password(field.data):
            raise ValidationError("wrong password")

    def update_user(self, user):
        user.password = self.new_password.data
        if user.save():
            return True
        else:
            return False




class SiteForm(FlaskForm):
    name = StringField(
            "Site Name",
            validators=[Required(), Length(2, 30), NameUniqueIn(Site)],
            render_kw={"autofocus": ''}
            )
    description = TextAreaField(
            "Description",
            validators=[Required(), Length(4, 200)]
            )
    submit = SubmitField("Submit")

    help_text = ["Normally, a site is related to a geography location, such as headquarter, a branch office, a factory, etc..."]



class NetworkForm(FlaskForm):
    address = StringField(
        "Network Address",
        render_kw={"placeholder": "10.0.0.0/8", "autofocus": ''},
    )
    description = TextAreaField(
        "Descrition",
        validators=[Required(), Length(2, 200)]
        )
    submit = SubmitField("Submit")


class AddNetworkForm(NetworkForm):
    def validate_address(self, field):
        try:
            ipaddress.ip_network(field.data)
        except:
            raise ValidationError("network address format wrong")
        this_network = ipaddress.ip_network(field.data)
        networks = Network.query.all()
        for network in networks:
            network = ipaddress.ip_network(network.address)
            if this_network.overlaps(network):
                raise ValidationError("network conflict")
    


class SubnetForm(FlaskForm):
    network_id = HiddenField(       # transfer network id to subnet form
        label = ''
        )
    name = StringField(
        "*Subnet Name",
        validators=[Length(2, 30)],
        render_kw={"autofocus": ''}
        )
    address = StringField(
        "*Subnet Address",
        render_kw={"placeholder": "10.10.1.0/24"},
        description="*slow on big size subnet"
        )
    gateway = StringField(
        "Gateway",
        )
    dns1 = StringField(
        "DNS1",
        validators=[IPAddress()]
        )
    dns2 = StringField(
        "DNS2",
        validators=[IPAddress()]
        )
    site_id = SelectField(
        "*Site", 
        coerce=int,
        validators=[Required()]
        )
    description = StringField(
        "*Description",
        validators=[Length(4, 200)]
        )
    vlan = IntegerField(
        "*VLAN ID",
        description="* 0 means not a VLAN",
        validators=[NumberRange(0, 4096)]
        )
    is_requestable = BooleanField(
        "allow user to request IP address from this subnet"
        )

    submit = SubmitField(
        "Submit",
        render_kw={
            "data-toggle": "modal",
            "data-target": "#loadingEffect",
            "data-backdrop": "static",
            "data-keyboard": "false"
        }
        )


    def validate_gateway(self, field):
        if field.data != '':
            try:
                ipaddress.ip_address(field.data)
            except:
                raise ValidationError("IP address format wrong")
            ip = ipaddress.ip_address(field.data)
            subnet = ipaddress.ip_network(self.address.data)
            if ip not in subnet:
                raise ValidationError("ip not in subnet")


class AddSubnetForm(SubnetForm):
    def validate_address(self, field):
        try:
            ipaddress.ip_network(field.data)
        except:
            raise ValidationError("network address format wrong")
        this_subnet = ipaddress.ip_network(field.data)
        n = Network.query.get_or_404(self.network_id.data)
        parent_network = ipaddress.ip_network(n.address)
        if not this_subnet.subnet_of(parent_network):
            raise ValidationError("not in network {}".format(n.address))
        subnets = Subnet.query.filter_by(network_id=self.network_id.data)
        for subnet in subnets:
            subnet = (ipaddress.ip_network(subnet.address))
            if this_subnet.overlaps(subnet):
                raise ValidationError("subnet conflict")



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



class SelectSiteForm(FlaskForm):
    site_id = SelectField(
        "please select your site", 
        coerce=int,
        validators=[Required()]
        )

    submit = SubmitField("Submit")



class SelectSubnetForm(FlaskForm):
    subnet_id = SelectField(
        "please select the subnet your need", 
        coerce=int,
        choices=[(0, '')],
        validators=[Required()]
        )

    submit = SubmitField("Submit")


class HostForm(FlaskForm):
    hostname = StringField(
        "*Device Name",
        validators=[Required(), Length(2, 128)]
        )
    mac_address = StringField(
        "*MAC Address",
        render_kw={"placeholder": "AA:BB:CC:11:22:33"},
        validators=[Required(), MacAddress()]
        )
    owner = StringField(
        "*Owner",
        validators=[Required(), Length(4, 64)]
        )
    owner_email = StringField(
        "*Owner E-mail",
        validators=[Required(), Email()]
        )
    description = TextAreaField(
        "Description",
        validators=[Length(4, 256)]
        )
    submit = SubmitField("Submit")





class CreateRequestForm(SelectSiteForm, SelectSubnetForm, HostForm):

    remark = None
    submit = SubmitField("Submit")



class AssignIPForm(FlaskForm):
    ip_id = SelectField(
        "assign IP",
        coerce=int,
        validators=[Required()]
        )

    submit = SubmitField("Submit")


