from flask import render_template, url_for, redirect, flash
from resurface import application, db
from flask_login import current_user, login_user, logout_user, login_required
from resurface.models import User, Item, Reminder
from resurface.forms import LoginForm, RegistrationForm, ReminderForm, ManualItemForm
from resurface.email import send_mail
from resurface.tasks import sched
from resurface.imports.pocket import pocket_import
from resurface.imports.youtube import youtube_import
from sqlalchemy.exc import IntegrityError
from datetime import datetime

@application.route('/', methods=['GET'])
def index():
    return render_template("index.html")

@application.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@application.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('home'))
    return render_template('login.html', title='Sign In', form=form)

@application.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@application.route("/home")
def home():
    items = current_user.items.all()
    return render_template(
        'home.html',
        num_saved_items=len(items),
        saved_items=sorted(items, key=lambda item: item.time_added, reverse=True)
    )

@application.route('/reminders', methods=['GET', 'POST'])
def reminders():
    form = ReminderForm()
    if current_user.is_authenticated:
        if form.validate_on_submit():
            sched.add_job(
                send_mail,
                kwargs={'email': current_user.email, 'num_items': form.num_items.data},
                trigger='cron',
                day_of_week=form.reminder_day.data,
                hour=form.reminder_time.data.hour,
                minute=form.reminder_time.data.minute
            )
            reminder_data = Reminder(
                user_id = current_user.id,
                reminder_day = form.reminder_day.data,
                reminder_time = form.reminder_time.data,
                reminder_items = form.num_items.data
            )
            db.session.add(reminder_data)
            db.session.commit()
            flash('Reminders succesfully changed!')
            return redirect(url_for('home'))
        return render_template(
                                'reminders.html',
                                form=form,
                                reminders=current_user.reminders.all()
                              )
    else:
        return redirect(url_for('login'))

@application.route("/import-items", methods=['GET', 'POST'])
def import_items():
    form = ManualItemForm()
    if form.validate_on_submit():
        db.session.add(
            Item(
                user_id=current_user.id,
                title=form.title.data,
                url=form.url.data,
                time_added=datetime.now(),
                source="manual"
            )
        )
        try:
            db.session.commit()
            flash('Item added successfully!')
        except IntegrityError:
            db.session.rollback()
            flash('Item already exists!')
        return redirect(url_for('import_items'))
    pocket_url = pocket_import()
    youtube_url = youtube_import()
    return render_template('import.html', pocket_url=pocket_url, youtube_url=youtube_url, form=form)

@application.route('/delete/<int:id>')
@login_required
def delete(id):
    post = Item.query.get(id)
    if post is None:
        flash('Post not found.')
        return redirect(url_for('home'))
    db.session.delete(post)
    db.session.commit()
    flash('Item deleted')
    return redirect(url_for('home'))