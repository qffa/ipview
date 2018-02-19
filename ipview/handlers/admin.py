from flask import Blueprint, render_template, url_for, redirect, flash, abort
from ipview.forms import SiteForm, AddSubnetForm
from ipview.models import db, Site, Subnet, Event
from flask_login import current_user



admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("/log")
def log():
    events = Event.query.order_by(Event.created_at.desc()).all()
    return render_template("admin/log.html", events=events)


@admin.route("/")
def index():
	return redirect(url_for("admin.site"))


@admin.route("/site")
def site():
    sites = Site.query.order_by(Site.site_name).all()
    return render_template("admin/site.html", sites=sites)


@admin.route("/site/add", methods=['GET', 'POST'])
def add_site():
    site = Site()
    form = SiteForm()
    if form.validate_on_submit():
        form.populate_obj(site)
        if site.save():
            site.log_event("Add new site: {}".format(site.site_name))
            flash("success", "success")
        else:
            flash("failed", "danger")

        return redirect(url_for("admin.site"))
    else:
        return render_template("admin/add_site.html", form=form)



@admin.route("/site/<int:site_id>/edit", methods=['GET', 'POST'])
def edit_site(site_id):
    site = Site.query.get_or_404(site_id)
    form = SiteForm(obj=site)
    if form.validate_on_submit():
        form.populate_obj(site)
        site.save()
        return redirect(url_for("admin.site"))
    else:
        return render_template("admin/edit_site.html", form=form, site_id=site_id)



@admin.route("/site/<int:site_id>/delete")
def delete_site(site_id):
    site = Site.query.get_or_404(site_id)
    if site.delete():
        site.log_event("Site is removed. site name: {}".format(site.site_name))
        flash("success", "success")
    else:
        flash("failed", "danger")

    return redirect(url_for("admin.site"))


@admin.route("/subnet")
def subnet():
    subnets = Subnet.query.all()
    return render_template("admin/subnet.html", subnets=subnets)


@admin.route("/subnet/add", methods=['GET', 'POST'])
def add_subnet():
    subnet = Subnet()
    form = AddSubnetForm()
    form.site_id.choices = [(site.id, site.site_name) for site in Site.query.order_by('site_name')]
    if form.validate_on_submit():
        form.populate_obj(subnet)
        subnet.save()
        return redirect(url_for("admin.subnet"))
    else:
        return render_template("/admin/add_subnet.html", form=form)



