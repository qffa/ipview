from flask import Blueprint, render_template, redirect, url_for


request = Blueprint('request', __name__, url_prefix="/request")



@request.route('/')
def index():
    return redirect(url_for("request.new"))


@request.route('/new')
def new():
	return render_template("request/new_request.html")



@request.route('/history')
def history():
	return render_template("request/h_request.html")
