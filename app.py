from flask import Flask, render_template, redirect, flash, session
from models import db, connect_db, User, Feedback
from flask_debugtoolbar import DebugToolbarExtension
from forms import Register, Login, UpdateFeedback, AddFeedback

app = Flask(__name__)
app.config['SECRET_KEY'] = "DHFGUSRGHUISHGUISHG"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)
connect_db(app)
db.create_all()

@app.route("/")
def redirect_to_register():
    return redirect("/register")

@app.route("/register", methods=["POST", "GET"])
def register():

    form = Register()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username, password, email, first_name, last_name)

        db.session.add(user)
        db.session.commit()
        if user:
            session["username"] = user.username
            flash("You made it!")
            return redirect("/users/"+str(user.username))
        else:
            form.username.errors = ["Invalid input."]

    else:
        return render_template("register.html", form=form)


@app.route("/login", methods=["POST", "GET"])
def authenticate():

    form = Login()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session["username"] = user.username
            flash("You made it!")
            return redirect("/users/"+str(user.username))
        else:
            form.username.errors = ["Invalid username or password."]
            return render_template("login.html", form=form)

    else:
        return render_template("login.html", form=form)

@app.route("/users/<username>")
def secret_page(username):
    if "username" not in session:
        flash("You must be logged in to view!")
        return redirect("/login")
    else:
        user = User.query.get(username)
        feedback = Feedback.query.filter(Feedback.username == username)
        return render_template("secret.html", user=user, feedback=feedback)

@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):

    username = User.query.get_or_404(username)

    db.session.delete(username)
    db.session.commit()
    session.pop("username")
    return redirect("/")


@app.route("/logout")
def logout():
    session.pop("username")

    return redirect("/")

@app.route("/feedback/<feedback_id>/delete", methods=["POST"])
def delete_feedback(feedback_id):

    feedback = Feedback.query.get_or_404(feedback_id)
    username = feedback.username

    db.session.delete(feedback)
    db.session.commit()
    return redirect(f'/users/{username}')

@app.route("/feedback/<feedback_id>/update", methods=["GET", "POST"])
def update_feedback(feedback_id):

    feedback = Feedback.query.get_or_404(feedback_id)
    form = UpdateFeedback(obj=feedback)

    if session["username"] == feedback.username:
        if form.validate_on_submit():

            feedback.title = form.title.data
            feedback.content = form.content.data

            db.session.commit()
            return redirect("/users/" + session["username"])
        else:
            return render_template("update_feedback.html", form=form)

    else:
        return redirect("/users/" + session["username"])

@app.route("/users/<username>/feedback/add", methods=["POST", "GET"])
def add_feedback(username):

    form = AddFeedback()

    if session["username"] == username:
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data

            feedback = Feedback(title, content, username)

            db.session.add(feedback)
            db.session.commit()

            return redirect(f"/users/{username}")
        else:
            return render_template("add_feedback.html", form=form)
    else:
        return redirect("/users/" + session["username"] + "/feedback/add")


