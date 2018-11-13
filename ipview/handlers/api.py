"""
File: api.py
Author: qffa
Description: ipview API, for client get data
"""


from flask import Blueprint, make_response
from ipview.models import Site, Subnet, IP
from flask.json import dumps
from sqlalchemy import and_




api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/site/<int:site_id>/subnets")
def subnets_of_site(site_id):
    """return subnets of given site
    """

    subnets = Subnet.query.filter_by(site_id=site_id).all()

    content_type = 'application/json; charset=utf-8'
    data = {}

    for subnet in subnets:
        data[subnet.id] = "{}({})".format(subnet.name, subnet.address)

    result = dumps(data) + '\n'
    code = 200
    response = make_response(result, code)
    response.headers['Content-Type'] = content_type

    return response

@api.route("/subnet/<int:subnet_id>/freeip/<int:count>")
def free_ip_of_subnet(subnet_id, count):
    """return free IP addresses from the given subnet
    """

    ips = IP.query.filter(IP.subnet_id==subnet_id, IP.is_inuse==False).limit(count).all()


    content_type = 'application/json; charset=utf-8'
    data = {}

    for ip in ips:
        data[ip.id] = ip.address

    result = dumps(data) + '\n'
    code = 200

    response = make_response(result, code)
    response.headers['Content-Type'] = content_type

    return response



