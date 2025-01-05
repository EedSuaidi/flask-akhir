from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    session,
    flash,
)
from . import db
from .models import User
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies,
)
from functools import wraps

main = Blueprint("main", __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please login first.", "warning")
            return redirect(url_for("main.login"))
        return f(*args, **kwargs)

    return decorated_function


def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id"):
            flash("You are already logged in.", "info")
            return redirect(url_for("main.get_users"))
        return f(*args, **kwargs)

    return decorated_function


@main.route("/")
def index():
    return redirect(url_for("main.get_users"))


@main.route("/register", methods=["GET", "POST"])
@logout_required
def register():
    if request.method == "POST":
        username = request.form["username"]
        role = request.form["role"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for("main.register"))

        if (
            User.query.filter_by(username=username).first()
            or User.query.filter_by(email=email).first()
        ):
            flash("User already exists.", "error")
            return redirect(url_for("main.register"))

        new_user = User(username=username, role=role, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")


@main.route("/login", methods=["GET", "POST"])
@logout_required
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            access_token = create_access_token(identity=str(user.id))

            session["user_id"] = user.id
            session["username"] = user.username
            session["role"] = user.role

            response = redirect(url_for("main.get_users"))
            set_access_cookies(response, access_token)
            flash("Login successful!", "success")
            return response

        flash("Invalid email or password!", "error")
    return render_template("login.html")


@main.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    session.clear()
    response = redirect(url_for("main.login"))
    unset_jwt_cookies(response)
    flash("You have been logged out.", "success")
    return response


@main.route("/dashboard/users", methods=["GET"])
@login_required
def get_users():
    users = User.query.all()
    users_data = [
        {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "email": user.email,
        }
        for user in users
    ]
    return render_template("get_users.html", users=users_data)


@main.route("/dashboard/users/create", methods=["GET", "POST"])
@login_required
def create_user():
    if request.method == "POST":
        username = request.form["username"]
        role = request.form["role"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for("main.register"))

        if (
            User.query.filter_by(username=username).first()
            or User.query.filter_by(email=email).first()
        ):
            flash("User already exists.", "error")
            return redirect(url_for("main.register"))

        new_user = User(username=username, role=role, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("User created successfully!", "success")
        return redirect(url_for("main.get_users"))

    return render_template("create_user.html")


@main.route("/dashboard/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        username = request.form["username"]
        role = request.form["role"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password and password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for("main.edit_user", user_id=user_id))

        if username:
            user.username = username
        if role:
            user.role = role
        if email:
            user.email = email
        if password:
            user.set_password(password)

        db.session.commit()
        flash("User updated successfully!", "success")
        return redirect(url_for("main.get_users"))

    return render_template("edit_user.html", user=user)


@main.route("/dashboard/users/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    if request.form.get("_method") == "DELETE":
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        flash("User deleted successfully!", "success")
        return redirect(url_for("main.get_users"))
    else:
        flash("Invalid request method.", "danger")
        return redirect(url_for("main.get_users"))
