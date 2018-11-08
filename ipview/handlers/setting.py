"""
File: setting.py
Author: qffa
Description: setting view functions

"""

from flask import Blueprint, render_template, redirect, url_for



setting = Blueprint("setting", __name__, url_prefix="/setting")



@setting.route('/')
def index():
	return redirect(url_for("setting.smtp"))


@setting.route('/smtp')
def smtp():
	return render_template("setting/smtp.html")
