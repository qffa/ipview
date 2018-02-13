from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError, TextAreaField, IntegerField
from wtforms.validators import Length, Email, EqualTo, Required
from ipview.models import db, Site


class AddSiteForm(FlaskForm):
    site_name = StringField("Site Name", validators=[Required(), Length(4, 30)])
    description = TextAreaField("Description", validators=[Required(), Length(4, 200)])
    submit = SubmitField("Submit")

    def add_site(self):
        site = Site()
        self.populate_obj(site)
        db.session.add(site)
        db.session.commit()
        flash("Site is added successfully")
        return site

    def validate_site_name(self, field):
        if Site.query.filter_by(site_name=field.data).first():
            raise ValidationError("Site exists")
