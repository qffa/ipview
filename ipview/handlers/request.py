from flask import Blueprint, render_template, redirect, url_for
from ipview.forms import SelectSiteForm
from ipview.models import db, Site, Host, Subnet


request = Blueprint('request', __name__, url_prefix="/request")



@request.route('/')
def index():
	return redirect(url_for("request.new"))

@request.route('/new')
def new():
    return render_template("request/new_request.html")

@request.route('/create', methods=['GET', 'POST'])
def create():
    if request.args.get("subnet"):
        pass
    elif request.args.get("site"):
        form = SelectSubnetForm()
        form.subnet_id.choices = [(subnet.id, "{}({})".format(subnet.name, subnet.address)) for site in Subnet.query.order_by("name")]
        if form.validate_on_submit():
            subnet_id = form.subnet_id.data
            return redirect(url_for("request.create", site=site_id, subnet=subnet_id))

        else:
            return render_template("request/create_request_2.html", form=form)
    else:
        form = SelectSiteForm()
        form.site_id.choices = [(site.id, site.name) for site in Site.query.order_by("name")]
        if form.validate_on_submit():
            site_id = form.site_id.data
            return redirect(url_for("request.create", site=site_id))

        else:
            return render_template("request/create_request.html", form=form)

@request.route('/history')
def history():
	return render_template("request/hist_request.html")






