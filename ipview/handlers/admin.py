import ipaddress
from sqlalchemy import and_
from flask import Blueprint, render_template, url_for, redirect, flash, abort, request
from ipview.forms import SiteForm, NetworkForm, SubnetForm, FilterForm, HostForm
from ipview.models import db, Site, Network, Subnet, IP, Event, Host
from flask_login import current_user
from wtforms.validators import Required



admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("/log")
def log():
    events = Event.query.order_by(Event.created_at.desc()).all()
    return render_template("admin/log.html", events=events)


@admin.route("/")
def index():
	return redirect(url_for("admin.network"))


## site functions

@admin.route("/site")
def site():
    """display all sites
    """
    sites = Site.query.order_by(Site.name).all()
    form = FilterForm()
    form.filter_by.choices = [("name", "site name"), ("description", "description")]
    return render_template("admin/site.html", sites=sites, form=form)


@admin.route("/site/add", methods=['GET', 'POST'])
def add_site():
    """add a new site
    """
    site = Site()
    form = SiteForm()
    if form.validate_on_submit():
        form.populate_obj(site)
        if site.save():
            site.log_event("Add new site: {}".format(site.name))
            flash("success", "success")
        else:
            flash("failed to add site", "danger")
        return redirect(url_for("admin.site"))
    else:
        return render_template("admin/add_site.html", form=form)


@admin.route("/site/<int:site_id>")
def site_detail(site_id):
    """display the subnets inside the site
    """
    url = request.url
    site = Site.query.get_or_404(site_id)
    return render_template("admin/site_detail.html", site=site, parent_url=url)


@admin.route("/site/<int:site_id>/edit", methods=['GET', 'POST'])
def edit_site(site_id):
    site = Site.query.get_or_404(site_id)
    form = SiteForm(obj=site)
    form.name.render_kw = {"readonly":''}
    form.name.validators = []
    if form.validate_on_submit():
        form.populate_obj(site)
        site.save()
        return redirect(url_for("admin.site"))
    else:
        return render_template("admin/edit_site.html", form=form, site_id=site_id)


@admin.route("/site/<int:site_id>/delete")
def delete_site(site_id):
    site = Site.query.get_or_404(site_id)
    if site.subnets == []:
        if site.delete():
            site.log_event("Removed site {}".format(site.name))
            flash("site is removed", "success")
        else:
            flash("failed to remove this site", "danger")
    else:
        flash("please remove the subnets under this site firstly", "danger")

    return redirect(url_for("admin.site"))


## network functions

@admin.route("/network")
def network():
    """display all networks(supernet CIDR)
    """
    networks = Network.query.all()
    return render_template("admin/network.html", networks=networks)


@admin.route("/network/add", methods=['GET', 'POST'])
def add_network():
    """add a new network
    """

    network = Network()
    form = NetworkForm()
    if form.validate_on_submit():
        form.populate_obj(network)
        network.address_pack = float(int(ipaddress.ip_network(network.address).network_address))
        if network.save():
            network.log_event("Add a new network: {}".format(network.address))
            flash("network added successfully", "success")
        else:
            flash("failed to add network", "danger")
        return redirect(url_for("admin.network"))
    else:
        return render_template("admin/add_network.html", form=form)


@admin.route("/network/<int:network_id>/edit", methods=['GET', 'POST'])
def edit_network(network_id):
    """edit the network by network id
    """

    network = Network.query.get_or_404(network_id)
    form = NetworkForm(obj=network)
    form.address.render_kw = {"readonly": ''}
    form.validate_address = None
    if form.validate_on_submit():
        form.populate_obj(network)
        network.save()
        return redirect(url_for("admin.network"))
    else:
        return render_template("admin/edit_network.html", form=form, network_id=network_id)


@admin.route("/network/<int:network_id>/delete")
def delete_network(network_id):
    """delete the network by supernet id
    """

    network = Network.query.get_or_404(network_id)
    if network.subnets == []:
        if network.delete():
            network.log_event("Removed network {}".format(network.address))
            flash("network is removed", "success")
        else:
            flash("failed to remove network", "danger")
    else:
        flash("please remove the sbunets under this network firstly", "danger")

    return redirect(url_for("admin.network"))


@admin.route("/network/<int:network_id>")
def network_detail(network_id):
    """display subnets inside the supernet
    """

    network = Network.query.get_or_404(network_id)
    url = request.url
    print(url)
    return render_template("admin/network_detail.html", network=network, parent_url=url)


## subnet functions

@admin.route("/subnet")
def subnet():
    """will retired
    """
    subnets = Subnet.query.all()
    return render_template("admin/subnet.html", subnets=subnets)


@admin.route("/network/<int:network_id>/addsubnet", methods=['GET', 'POST'])
def add_subnet_under(network_id):
    """add new subnet
    """
    subnet = Subnet()
    network = Network.query.get_or_404(network_id)
    form = SubnetForm()
    form.network_id.data = network_id
    form.site_id.choices = [(site.id, site.name) for site in Site.query.order_by('name')]
    if form.validate_on_submit():
        form.populate_obj(subnet)
        subnet.network = network    # link to foreign key: network
        subnet.address_pack = float(int(ipaddress.ip_network(subnet.address).network_address))
        # after subnet created, write all its IP addresses into database IP table
        if subnet.save():  
            subnet_scope = ipaddress.ip_network(subnet.address)    # ip_network obj for this subnet
            for ip_addr in subnet_scope.hosts():
                ip = IP()
                ip.address = ip_addr.compressed
                ip.subnet = subnet
                db.session.add(ip)
            try:
                db.session.commit()
            except:
                db.session.rollback()
                subnet.delete()
                flash("failed to create IP addresses.", "danger")

        if Subnet.query.filter_by(address=subnet.address):
            subnet.log_event("Add new subnent: {}".format(subnet.address))
        else:
            flash("failed to add subnet", "danger")

        return redirect(url_for("admin.network_detail", network_id=network.id))
    else:
        return render_template("/admin/add_subnet.html", form=form, network=network)


@admin.route("/subnet/<int:subnet_id>/edit", methods=['GET', 'POST'])
def edit_subnet(subnet_id):
    """edit the subnet
    """
    subnet = Subnet.query.get_or_404(subnet_id)
    form = SubnetForm(obj=subnet)
    form.site_id.choices = [(site.id, site.name) for site in Site.query.order_by('name')]
    form.address.render_kw = {"readonly": ''}
    self_url = request.url
    parent_url = request.args.get('next')
    if form.validate_on_submit():
        form.populate_obj(subnet)
        subnet.save()
        return parent_url or url_for("admin.network")
    else:
        return render_template("admin/edit_subnet.html", form=form, self_url=self_url, parent_url=parent_url, subnet_id=subnet_id)


@admin.route("/subnet/<int:subnet_id>/delete")
def delete_subnet(subnet_id):
    """delete subnet and IP addresses in it.
    """
    parent_url = request.args.get('next')
    if IP.query.filter(and_(IP.subnet_id==subnet_id, IP.is_inuse==True)).first():
        flash("please remove the host under this subnet firstly", "danger")
    else:
        subnet = Subnet.query.get_or_404(subnet_id)
        for ip in subnet.ips:
            db.session.delete(ip)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            flash("IP addresses removed failed", "danger")
        if subnet.delete():
            subnet.log_event("Subnet {} is removed.".format(subnet.address))
            flash("success", "success")
        else:
            flash("subnet remove failed", "danger")
    
    return redirect(parent_url or url_for("admin.network"))


@admin.route("/<parent>/<int:parent_id>/subnet/<int:subnet_id>")
def subnet_detail(parent, parent_id, subnet_id):
    """display all IP addresses in this subnet.
    """
    if parent == 'network':
        parent_obj = Network.query.get_or_404(parent_id)
    elif parent == 'site':
        parent_obj = Site.query.get_or_404(parent_id)
    subnet = Subnet.query.get_or_404(subnet_id)
    url = request.url
    return render_template("admin/subnet_detail.html", parent=parent, subnet=subnet, parent_url=url)



## IP functions

@admin.route("/ip/<int:ip_id>/assign", methods=['GET', 'POST'])
def assign_ip(ip_id):
    """assign IP address to host
    """
    parent_url = request.args.get('next')
    ip = IP.query.get_or_404(ip_id)
    if ip.is_inuse:
        flash("already assign to a host", "danger")
        return redirect(parent_url)
    host = Host()
    form = HostForm()
    self_url = request.url
    if form.validate_on_submit():
        form.populate_obj(host)
        ip.is_inuse = True
        host.ip = ip
        if ip.save() and host.save():
            host.log_event("Assign IP {} to host {}".format(ip.address, host.name))
            flash("IP assigned", "success")
        else:
            flash("failed to assign this IP", "danger")
        return redirect(parent_url or url_for("admin.network"))
    else:
        return render_template("admin/assign_ip.html", ip=ip, form=form, self_url=self_url, parent_url=parent_url)


@admin.route("/ip/<int:ip_id>/release")
def release_ip(ip_id):
    """release this IP address
    """
    parent_url = request.args.get('next')
    ip = IP.query.get_or_404(ip_id)
    if ip.host:
        ip.host.delete()
        ip.is_inuse = False
        ip.save()
        flash("IP released", "success")
        
    return redirect(parent_url)


@admin.route("/ip/<int:ip_id>/edit")
def edit_ip(ip_id):
    """edit the host info on this ip
    """

    pass













