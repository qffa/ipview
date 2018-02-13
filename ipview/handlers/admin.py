from flask import Blueprint, render_template, url_for, redirect
from ipview.forms import AddSiteForm
from ipview.models import Site



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



@admin.route("/admin/<int:site_id>/edit", methods=['GET', 'POST'])
def edit_site(site_id):
    pass



@admin.route("/admin/<int:site_id>/delete")
def delete_site(site_id):
    pass



