from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, ValidationError, TextAreaField, IntegerField
from wtforms.validators import Length, Email, EqualTo, Required
from ipview.models import db, Site, Subnet


class SiteForm(FlaskForm):
    id = IntegerField("id")
    site_name = StringField("Site Name", validators=[Required(), Length(4, 30)])
    description = TextAreaField("Description", validators=[Required(), Length(4, 200)])
    submit = SubmitField("Submit")

    def update_db(self, site):
        self.populate_obj(site)
        db.session.add(site)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            flash("Site name exist.", "danger")
            return site
        else:
            flash("Site is added successfully", "success")
            return site

'''
    def validate_site_name(self, field):
        if Site.query.filter_by(site_name=field.data).first():
            raise ValidationError("Site exists")
'''


class AddSubnetForm(FlaskForm):
    id = IntegerField("id")
    subnet_name = StringField("Subnet Name", validators=[Required(), Length(4, 30)])
    subnet_address = StringField("Subnet Address", render_kw={"placeholder": "192.168.1.0/24"}, validators=[Required(), Length(4, 60)])
    gateway = StringField("Gateway", validators=[Length(4, 60),])
    dns = StringField("DNS", validators=[Length(4, 200)])
    site_id = SelectField("Site", coerce=int, validators=[Required()])
    description = StringField("Description", validators=[Length(4, 200)])
    vlan = IntegerField("VLAN ID", description="* 0 means no VLAN", validators=[])
    submit = SubmitField("Submit")

    def add_subnet(self):
        subnet = Subnet()
        self.populate_obj(subnet)
        db.session.add(subnet)
        db.session.commit()
        flash("Subnet is added successfully", "success")
        return subnet




