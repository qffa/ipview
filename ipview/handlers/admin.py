from flask import Blueprint, render_template, url_for, redirect
from ipview.forms import AddSiteForm, AddSubnetForm
from ipview.models import Site, Subnet



admin = Blueprint("admin", __name__, url_prefix="/admin")



@admin.route("/")
def index():
	return redirect(url_for("admin.site"))


@admin.route("/site")
def site():
    sites = Site.query.all()
    return render_template("admin/site.html", sites=sites)


@admin.route("/site/add", methods=['GET', 'POST'])
def add_site():
    form = AddSiteForm()
    if form.validate_on_submit():
        form.add_site()
        return redirect(url_for("admin.site"))
    else:
        return render_template("admin/add_site.html", form=form)



@admin.route("/site/<int:site_id>/edit", methods=['GET', 'POST'])
def edit_site(site_id):
    pass



@admin.route("/site/<int:site_id>/delete")
def delete_site(site_id):
    pass


@admin.route("/subnet")
def subnet():
    subnets = Subnet.query.all()
    return render_template("admin/subnet.html", subnets=subnets)


@admin.route("/subnet/add", methods=['GET', 'POST'])
def add_subnet():
    form = AddSubnetForm()
    form.site_id.choices = [(site.id, site.site_name) for site in Site.query.order_by('site_name')]
    if form.validate_on_submit():
        form.add_subnet()
        return redirect(url_for("admin.subnet"))
    else:
        return render_template("/admin/add_subnet.html", form=form)



