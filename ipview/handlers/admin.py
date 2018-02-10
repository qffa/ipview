from flask import Blueprint, render_template, url_for, redirect
from ipview.forms import AddSiteForm



admin = Blueprint("admin", __name__, url_prefix="/admin")



@admin.route("/")
def index():
	return redirect(url_for("admin.site"))


@admin.route("/site")
def site():
    return render_template("admin/site.html")


@admin.route("/site/add", methods=['GET', 'POST'])
def add():
    form = AddSiteForm()
    if form.validate_on_submit():
        form.add_site()
        return redirect(url_for("site.index"))
    else:
        return render_template("admin/add_site.html", form=form)



@admin.route("/admin/<int:site_id>/edit", methods=['GET', 'POST'])
def edit(site_id):
    pass



@admin.route("/admin/<int:site_id>/delete")
def delete(site_id):
    pass



