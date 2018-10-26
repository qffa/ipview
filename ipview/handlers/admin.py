import ipaddress
from flask import Blueprint, render_template, url_for, redirect, flash, abort
from ipview.forms import SiteForm, NetworkForm, AddSubnetForm, FilterForm
from ipview.models import db, Site, Network, Subnet, IP, Event
from flask_login import current_user



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
    site = Site.query.get_or_404(site_id)
    return render_template("admin/site_detail.html", site=site)


@admin.route("/site/<int:site_id>/edit", methods=['GET', 'POST'])
def edit_site(site_id):
    site = Site.query.get_or_404(site_id)
    form = SiteForm(obj=site)
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
        network.address_pack = int(ipaddress.ip_network(network.address).network_address)
        if network.save():
            network.log_event("Add a new network: {}".format(network.address))
            flash("network added successfully", "success")
        else:
            flash("failed to add network", "danger")
        return redirect(url_for("admin.network"))
    else:
        return render_template("admin/add_network.html", form=form)


@admin.route("/network/<int:network_id>/edit")
def edit_network(network_id):
    """edit the network by network id
    """

    pass


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
    return render_template("admin/network_detail.html", network=network)


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
    form = AddSubnetForm()
    form.site_id.choices = [(site.id, site.name) for site in Site.query.order_by('name')]
    if form.validate_on_submit():
        form.populate_obj(subnet)
        subnet.network = network    # link to foreign key: network
        subnet.address_pack = int(ipaddress.ip_network(subnet.address).network_address)
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


@admin.route("/subnet/<int:subnet_id>/edit")
def edit_subnet(subnet_id):
    """edit the subnet
    """
    pass


@admin.route("/subnet/<int:subnet_id>/delete")
def delete_subnet(subnet_id):
    """delete subnet and IP addresses in it.
    """
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
    
    return redirect(url_for("admin.subnet"))


@admin.route("/<father>/<int:father_id>/subnet/<int:subnet_id>")
def subnet_detail(father, father_id, subnet_id):
    """display all IP addresses in this subnet.
    """
    if father == 'network':
        father_obj = Network.query.get_or_404(father_id)
    elif father == 'site':
        father_obj = Site.query.get_or_404(father_id)
    subnet = Subnet.query.get_or_404(subnet_id)
    return render_template("admin/subnet_detail.html", father=father, subnet=subnet)







