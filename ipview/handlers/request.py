from flask import Blueprint, render_template, redirect, url_for
from flask import request as http_request
from ipview.forms import SelectSiteForm, SelectSubnetForm, HostForm
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
    url = http_request.url
    if http_request.args.get("subnet"):
        form = HostForm()
        if form.validate_on_submit():
            pass
        else:
            return render_template("request/create_request_step3.html", form=form, url=url)
        pass
    elif http_request.args.get("site"):
        form = SelectSubnetForm()
        form.subnet_id.choices = [
                (subnet.id, "{}({})".format(subnet.name, subnet.address)) for subnet in Subnet.query.filter_by(site_id=http_request.args.get("site")).order_by("name")
                ]
        if form.validate_on_submit():
            subnet_id = form.subnet_id.data
            return redirect(url + "&subnet={}".format(subnet_id))

        else:
            return render_template("request/create_request_step2.html", form=form, url=url)
    else:
        form = SelectSiteForm()
        form.site_id.choices = [(site.id, site.name) for site in Site.query.order_by("name")]
        if form.validate_on_submit():
            site_id = form.site_id.data
            return redirect(url + "&site={}".format(site_id))

        else:
            return render_template("request/create_request_step1.html", form=form, url=url)

@request.route('/history')
def history():
	return render_template("request/hist_request.html")






