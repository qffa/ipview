from flask import Blueprint, render_template, url_for, redirect
from ipview.forms import AddSiteForm



site = Blueprint("site", __name__, url_prefix="/site")



@site.route("/")
def index():
    return render_template("site/index.html")


@site.route("/add", methods=['GET', 'POST']):
def add():
    form = AddSiteForm()
    if form.validate_on_submit():
        form.add_site()
        return redirect(url_for("site.index"))
    else:
        return render_template("site/add_site.html", form=form)


@site.route("/<int:site_id>/edit", methods=['GET', 'POST']):
def edit(site_id):
    pass



@site.route("/<int:site_id>/delete")
def delete(site_id):
    pass



