import ipaddress
from flask import Blueprint, render_template, url_for, redirect, flash, abort
from ipview.forms import SiteForm, AddSubnetForm, FilterForm
from ipview.models import db, Site, Subnet, IP, Event
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
    form = FilterForm()
    form.filter_by.choices = [("site_name", "site name"), ("description", "description")]
    return render_template("admin/site.html", sites=sites, form=form)


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
            flash("failed to add site", "danger")

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
        flash("site remove failed", "danger")

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
        if subnet.save():
            subnet_network = ipaddress.ip_network(subnet.subnet_address)    # ip_network obj for this subnet
            for ip_addr in subnet_network.hosts():
                ip = IP()
                ip.ip_address = ip_addr.exploded
                ip.subnet = subnet
                db.session.add(ip)
            try:
                db.session.commit()
                subnet.log_event("Add new subnent: {}".format(subnet.subnet_address))
            except:
                db.session.rollback()
                subnet.delete()
                flash("failed to create IP addresses.", "danger")
        else:
            flash("failed to add subnet", "danger")
        return redirect(url_for("admin.subnet"))
    else:
        return render_template("/admin/add_subnet.html", form=form)


@admin.route("/subnet/<int:subnet_id>/edit")
def edit_subnet():
    pass


@admin.route("/subnet/<int:subnet_id>/delete")
def delete_subnet(subnet_id):
    """delete subnet and IP addresses in it.
    """
    subnet = Subnet.query.get_or_404(subnet_id)
    for ip in subnet.ips:
        db.session.delete(ip)
    try:
        db.session.commit()
    except:
        db.session.rollback()
        flash("IP addresses removed failed", "danger")
    if subnet.delete():
        subnet.log_event("Subnet {} is removed.".format(subnet.subnet_address))
        flash("success", "success")
    else:
        flash("subnet remove failed", "danger")
    
    return redirect(url_for("admin.subnet"))


@admin.route("/subnet/<int:subnet_id>")
def subnet_detail(subnet_id):
    """display all IP addresses in this subnet.
    """
    subnet = Subnet.query.get_or_404(subnet_id)
    return render_template("admin/subnet_detail.html", subnet=subnet)
