import os
from flask import Flask, render_template, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap5
from tables import *
from sqlalchemy.exc import NoResultFound, IntegrityError
from turbo_flask import Turbo
from forms import NewTask, RegisterForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from datetime import datetime, timedelta, timezone
import psycopg2


# Some Constants
time_zone = timezone(timedelta(hours=5, minutes=30))

# Initializing Flask app
app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']

# Initializing Bootstrap
bootstrap = Bootstrap5()
bootstrap.init_app(app)

# Initializing Turbo
turbo = Turbo()
turbo.init_app(app)

# Creating database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URI"]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Initializing Login Manager
login_manager = LoginManager()
login_manager.init_app(app)

# creating tables in app context
with app.app_context():
    db.create_all()


# Creating User
@login_manager.user_loader
def load_user(user_id):
    try:
        cur_user = db.session.execute(db.select(User).filter_by(id=int(user_id))).scalar_one()
    except NoResultFound:
        cur_user = None
    return cur_user


def divide_tasks(tasks: list[Todo]) -> tuple[list[Todo], list[Todo], list[Todo], list[Todo]]:
    tasks_to_do = []
    working_on = []
    complete = []
    archived = []
    for task in tasks:
        if not task.task_started:
            tasks_to_do.append(task)
        elif not task.task_finished:
            working_on.append(task)
        elif not task.archived:
            complete.append(task)
        else:
            archived.append(task)

    return tasks_to_do, working_on, complete, archived


@app.route('/', methods=['GET', 'POST'])
def home():
    form = NewTask()
    if form.validate_on_submit():
        new_task = Todo(task=form.task.data,
                        estimated_end_date=form.estimated_end_date.data,
                        user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()

    if current_user.is_authenticated:
        try:
            todo_list = list(db.session.execute(db.select(Todo)
                                                .filter_by(user_id=current_user.id)
                                                .order_by(Todo.estimated_end_date))
                             .scalars())
        except AttributeError:
            todo_list = []
        form = NewTask(formdata=None)

        # Dividing tasks into tasks_todo, working_on and completed
        tasks_to_do, working_on, complete, archived = divide_tasks(todo_list)
        session['name'] = current_user.name
        return render_template('index.html',
                               form=form,
                               tasks_to_do=tasks_to_do,
                               working_on=working_on,
                               completed=complete,
                               archive=archived
                               )
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=16)
        )
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            flash("You are already registered.")
            return redirect(url_for('register'))
        else:
            login_user(new_user)
            session['name'] = new_user.name
            flash(f"Welcome {new_user.name.title()}. You are logged in.")
            return redirect(url_for('home'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_email = form.email.data
        user_password = form.password.data
        try:
            user = db.session.execute(db.select(User).filter_by(email=user_email)).scalar_one()
        except NoResultFound:
            flash("Wrong Email! Email is not registered.")
            return redirect(url_for('login'))

        if check_password_hash(user.password, user_password):
            login_user(user)
            session['name'] = user.name
            flash(f"Welcome back {user.name.title()}. You are logged in.")
            return redirect(url_for('home'))
        else:
            flash("Wrong Password!")
            return redirect(url_for('login'))

    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash("You are logged out.")
    return redirect(url_for('home'))


# Insert some variables in website
@app.context_processor
def inject_variables():
    cur_year = datetime.now().year
    return dict(year=cur_year)


# list modifying functions
@app.route('/start/<int:task_id>')
def start(task_id):
    task = db.get_or_404(Todo, task_id)
    task.task_started = True
    task.start_date = datetime.now(tz=time_zone)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/delete/<int:task_id>')
def delete(task_id):
    task = db.get_or_404(Todo, task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/completed/<int:task_id>')
def completed(task_id):
    task = db.get_or_404(Todo, task_id)
    task.task_finished = True
    task.end_date = datetime.now(tz=time_zone)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/archive/<int:task_id>')
def archive(task_id):
    task = db.get_or_404(Todo, task_id)
    task.archived = True
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/stopped/<int:task_id>')
def stopped(task_id):
    task = db.get_or_404(Todo, task_id)
    task.task_started = False
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/unarchive/<int:task_id>')
def unarchive(task_id):
    task = db.get_or_404(Todo, task_id)
    task.archived = False
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/not_complete/<int:task_id>')
def not_complete(task_id):
    task = db.get_or_404(Todo, task_id)
    task.task_finished = False
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run()
