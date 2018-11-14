"""
File: request.py
Author: qffa
Description: request view functions

"""


from flask import Blueprint, render_template, redirect, url_for, abort
from flask import request as http_request
from flask_login import current_user
from sqlalchemy import and_
from ipview.forms import SelectSiteForm, SelectSubnetForm, HostForm, CreateRequestForm
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


    form = CreateRequestForm()
    form.site_id.choices = [(site.id, site.name) for site in Site.query.order_by("name")]
    form.subnet_id.choices = [
            (subnet.id, "{}".format(subnet.name))\
            for subnet in Subnet.query.filter(Subnet.is_requestable==True)
            ]
    owner = http_request.args.get("owner")
    if owner == "self":
        owner = current_user
        form.owner.data = current_user.username
        form.owner_email.data = current_user.email
    if form.validate_on_submit():
        host = Host()
        request = Request()
        form.populate_obj(host)
        request.request_subnet_id = form.subnet_id.data
        request.host = host
        request.user_id = current_user.id
        DBTools.save_all(host, request)
        return render_template("request/create_request_success.html")

    else:
        form.subnet_id.choices = []
        return render_template("request/create_request_step1.html", form=form)




@request.route('/history')
def history():
    """display request history
    """
    requests = Request.query.filter_by(user_id=current_user.id).order_by(Request.created_at.desc()).all()
    url = http_request.url
    return render_template("request/hist_request.html", requests=requests, parent_url=url)



@request.route("/<int:request_id>/detail")
def request_detail(request_id):
    """dispaly request detail info
    """
    parent_url = http_request.args.get("next")
    request = Request.query.get_or_404(request_id)
    if request.user.id != current_user.id:
        return abort(404)

    return render_template("request/request_detail.html", request=request, parent_url=parent_url)



