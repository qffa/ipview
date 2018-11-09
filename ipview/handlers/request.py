"""
File: request.py
Author: qffa
Description: request view functions

"""


from flask import Blueprint, render_template, redirect, url_for, abort
from flask import request as http_request
from flask_login import current_user
from sqlalchemy import and_
from ipview.forms import SelectSiteForm, SelectSubnetForm, HostForm
from ipview.models import db, DBTools, Site, Host, Subnet, Request


request = Blueprint('request', __name__, url_prefix="/request")



@request.route('/test')
def test():
    """
    for dev test page
    """
    return render_template("request/create_request_success.html")

@request.route('/')
def index():
	return redirect(url_for("request.new"))

@request.route('/new')
def new():
    """display new request page
    """
    return render_template("request/new_request.html")

@request.route('/create', methods=['GET', 'POST'])
def create():
    """create new request
    """
    url = http_request.url
    if http_request.args.get("subnet"):     ## step 3
        form = HostForm()
        owner = http_request.args.get("owner")
        if owner == "self":
            owner = current_user
            form.owner.data = current_user.username
            form.owner_email.data = current_user.email
        if form.validate_on_submit():
            host = Host()
            request = Request()
            form.populate_obj(host)
            host.request_subnet_id = http_request.args.get("subnet")
            request.host = host
            request.user_id = current_user.id
            DBTools.save_all(host, request)
            return render_template("request/create_request_success.html")
        else:
            return render_template("request/create_request_step3.html", form=form, url=url)
    elif http_request.args.get("site"):     ## step 2
        form = SelectSubnetForm()
        form.subnet_id.choices = [
                (subnet.id, "{}({})".format(subnet.name, subnet.address))\
                for subnet in Subnet.query.filter(and_(Subnet.is_requestable==True, Subnet.site_id==http_request.args.get("site"))).\
                    order_by("name")
                ]
        if form.validate_on_submit():
            subnet_id = form.subnet_id.data
            return redirect(url + "&subnet={}".format(subnet_id))

        else:
            return render_template("request/create_request_step2.html", form=form, url=url)
    else:   ## step 1
        form = SelectSiteForm()
        form.site_id.choices = [(site.id, site.name) for site in Site.query.order_by("name")]
        if form.validate_on_submit():
            site_id = form.site_id.data
            return redirect(url + "&site={}".format(site_id))

        else:
            return render_template("request/create_request_step1.html", form=form, url=url)

@request.route('/history')
def history():
    """display request history
    """
    requests = Request.query.filter_by(user_id=current_user.id).order_by(Request.created_at.desc()).all()
    url = http_request.url
    return render_template("request/hist_request.html", requests=requests, parent_url=url)



@request.route("/host/<int:host_id>/detail")
def host_detail(host_id):
    """dispaly host detail info
    """
    parent_url = http_request.args.get("next")
    host = Host.query.get_or_404(host_id)
    if not host.request:
        return abort(404)
    elif host.request.user.id != current_user.id:
        return abort(404)

    return render_template("request/host_detail.html", host=host, parent_url=parent_url)



