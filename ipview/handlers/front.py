"""for login and index page
file name: front.py

"""


from flask import Blueprint, render_template, redirect, url_for
from ipview.forms import LoginForm
from flask_login import login_required, login_user, logout_user, current_user
from ipview.models import User



front = Blueprint('front', __name__)


@front.route('/')
@login_required
def index():
    if current_user.is_admin:
        return redirect(url_for("admin.waiting_request"))
    else:
        return redirect(url_for("request.new"))


@front.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        login_user(user)
        return redirect(url_for('front.index'))

    else:
        return render_template('login.html', form=form)
