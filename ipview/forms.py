import re
import ipaddress
from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, ValidationError, TextAreaField, IntegerField, HiddenField
from wtforms.validators import Length, Email, EqualTo, Required, NumberRange, MacAddress, IPAddress
from ipview.models import db, Site, Network, Subnet, User


class validate_tools():

    @staticmethod
    def verify_ip_address(ip):
        if not ip == '':
            try:
                ipaddress.ip_address(ip)
            except:
                raise ValidationError("wrong IP format!")

    @staticmethod
    def verify_ip_network(network):
        try:
            ipaddress.ip_network(network)
        except:
            raise ValidationError("wrong subnet format!")

    @staticmethod
    def overlaps_ip_network(network, other_network):
        if network.overlaps(other_network):
            raise ValidationError("subnet conflict")


    @staticmethod
    def verify_ip_in_subnet(ip, subnet):
        if ip not in subnet:
            raise ValidationError("Gateway is not in the subnet.")



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
    name = StringField(
            "Site Name",
            validators=[Required(), Length(4, 30)],
            render_kw={"autofocus": ''}
            )
    description = TextAreaField(
            "Description",
            validators=[Required(), Length(4, 200)]
            )
    submit = SubmitField("Submit")

    def validate_name(self, field):
        if Site.query.filter_by(name=field.data).first():
            raise ValidationError("Site exists")


class NetworkForm(FlaskForm):
    address = StringField(
        "Network Address",
        render_kw={"placeholder": "10.0.0.0/8", "autofocus": ''},
        validators=[Required(), Length(4, 60)],
    )
    description = TextAreaField(
        "Descrition",
        validators=[Required(), Length(4, 200)]
        )
    submit = SubmitField("Submit")

    def validate_address(self, field):
        validate_tools.verify_ip_network(field.data)
        networks = Network.query.all()
        this_network = ipaddress.ip_network(field.data)
        for network in networks:
            network = ipaddress.ip_network(network.address)
            validate_tools.overlaps_ip_network(this_network, network)



class SubnetForm(FlaskForm):
    network_id = HiddenField(       # transfer network id to subnet form
        label = None
        )
    name = StringField(
        "*Subnet Name",
        validators=[Required(), Length(4, 30)],
        render_kw={"autofocus": ''}
        )
    address = StringField(
        "*Subnet Address",
        render_kw={"placeholder": "10.10.1.0/24"},
        validators=[Required(), Length(4, 60)],
        description="*slow on big size subnet"
        )
    gateway = StringField(
        "Gateway",
        validators=[]
        )
    dns1 = StringField(
        "DNS1",
        validators=[]
        )
    dns2 = StringField(
        "DNS2",
        validators=[]
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
    submit = SubmitField(
        "Submit"
        )

    """
    render_kw={
        "data-toggle": "modal",
        "data-target": "#myModal",
        "data-backdrop": "static",
        "data-keyboard": "false"
    }
    """

    def validate_address(self, field):
        validate_tools.verify_ip_network(field.data)
        this_subnet = ipaddress.ip_network(field.data)
        n = Network.query.get_or_404(self.network_id.data)
        parent_network = ipaddress.ip_network(n.address)
        if this_subnet not in parent_network:
            raise ValidationError("not in network {}".format(n.address))
        subnets = Subnet.query.filter_by(network_id=self.network_id.data)    # need to narrow to this supernet
        for subnet in subnets:
            subnet = (ipaddress.ip_network(subnet.address))
            validate_tools.overlaps_ip_network(this_subnet, subnet)
    def validate_dns1(self, field):
        validate_tools.verify_ip_address(field.data) 

    def validate_dns2(self, field):
        validate_tools.verify_ip_address(field.data) 
    def validate_gateway(self, field):
        validate_tools.verify_ip_address(field.data)
        if field.data != '':
            ip = ipaddress.ip_address(field.data)
            subnet = ipaddress.ip_network(self.address.data)
            validate_tools.verify_ip_in_subnet(ip, subnet)



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




class HostForm(FlaskForm):
    name = StringField(
        "*Device Name",
        validators=[Required(), Length(4, 128)],
        render_kw={"autofocus": ''}
        )
    mac_address = StringField(
        "*MAC Address",
        render_kw={"placeholder": "AA:BB:CC:11:22:33"},
        validators=[Required(),]
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

    def validate_mac_address(self, field):
        if not re.match(r"^\s*([0-9a-fA-F]{2,2}:){5,5}[0-9a-fA-F]{2,2}\s*$", field.data):
            raise ValidationError("MAC address format wrong")





