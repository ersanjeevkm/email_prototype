from flask import render_template, url_for, flash, redirect, request, abort
from email_prototype.forms import Login, Signup, Account, Newmail, Editdraft, Resetrequest, Passwordreset
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from email_prototype import app, bcrypt, db, mail
from email_prototype.db_models import User, Inbox, Outbox, Draft
from PIL import Image
import secrets
import os

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user_inbox'))
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                flash("You are successfully logged in! ", 'success')
                next = request.args.get('next')
                if next:
                    return redirect(next)
                return redirect(url_for('user_inbox'))
            else:
                flash('Password incorrect! Try again', 'danger')
        else:
            flash('Email incorrect! Try again', 'danger')
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET','POST'])
def signup():
    form = Signup()
    if current_user.is_authenticated:
        return redirect(url_for('user_mails'))
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password=hashed)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {user.username}, Login to continue. ', 'success')
        msg = '''We are pleased to have you here. As said in the home page its just a pototype.
Don't use your original credentials here and not for personal purpose. Enjoy ✌😊

From Sanjeev's email-prototype team, Cheers!!! 
'''
        inbox = Inbox(subject="Welcome to Sanjeev's email prototype", message=msg, sender='noreply@sanjeev.com')
        inbox.Inboxuser = user
        db.session.add(inbox)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

def save_pic(form_pic):
    random = secrets.token_hex(8)
    _, ext = os.path.splitext(form_pic.filename)
    name = random + ext
    pic_fn = os.path.join(app.root_path, 'static/profile_pics', name)
    output_size = (125, 125)
    i = Image.open(form_pic)
    i.thumbnail(output_size)
    i.save(pic_fn)
    return name

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = Account()
    if form.validate_on_submit():
        user = User.query.get(current_user.id)
        user.username = form.username.data
        user.email = form.email.data
        if form.picture.data:
            name = save_pic(form.picture.data)
            if user.picture != 'demo.jpg':
                os.remove(os.path.join(app.root_path, 'static/profile_pics', user.picture))
            user.picture = name
        db.session.commit()
    else:
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', form=form)

def send_mail(user, email):
    token = user.reset_request()
    msg = Message('Password reset request', recipients=[email], sender='noreply@demo.com')
    msg.body = f'''Your request for password reset. Follow the below link to continue
{url_for('password_reset', token=token, _external=True)}

This link is valid only for 30 min. 
If you didn't mke the request, don't worry just ignore it.

From Sanjeev's email prototype team. Cheers!!!
    '''
    mail.send(msg)

@app.route('/account/reset_request', methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('user_inbox'))
    else:
        form = Resetrequest()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            send_mail(user, form.pass_email.data)
            flash(f'We have successfully sent an password reset link to your mail-id : {form.pass_email.data}', 'success')
        return render_template('reset_request.html', form=form)

@app.route('/account/password_reset/<token>', methods=['GET','POST'])
def password_reset(token):
    if current_user.is_authenticated:
        return redirect(url_for('user_inbox'))
    else:
        if User.reset_password(token) is None:
            flash('The current token is invalid/expired. Try again', 'warning')
            return redirect(url_for('reset_request'))
        else:
            form = Passwordreset()
            if form.validate_on_submit():
                id = User.reset_password(token)
                user = User.query.get(id)
                hash = bcrypt.generate_password_hash(form.password.data)
                user.password = hash
                db.session.commit()
                flash("Your password has been changed. Login using your new password", 'success')
                return redirect(url_for('login'))
            return render_template('password_reset.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('home'))

#mails

@app.route('/mail/new', methods=['GET', 'POST'])
@login_required
def new_mail():
    form = Newmail()
    if form.validate_on_submit():
        if form.draft.data:
            draft = Draft(subject=form.subject.data, message=form.message.data, receiver=form.receiver.data)
            draft.Draftuser = current_user
            db.session.add(draft)
            db.session.commit()
            flash(f'Message successfully saved to draft. ', 'success')
            return redirect(url_for('user_draft'))

        inbox = Inbox(subject=form.subject.data, message=form.message.data, sender=current_user.email)
        inbox.Inboxuser = User.query.filter_by(email=form.receiver.data).first()
        db.session.add(inbox)

        outbox = Outbox(subject=form.subject.data, message=form.message.data, receiver=form.receiver.data)
        outbox.Outboxuser = current_user
        db.session.add(outbox)

        db.session.commit()
        flash(f'Message sent successfully to {form.receiver.data}', 'success')
        return redirect(url_for('user_outbox'))
    return render_template('new_mail.html', form=form)


@app.route('/mail/inbox')
@login_required
def user_inbox():
    page = request.args.get('page', 1, type=int)
    mails = Inbox.query.filter_by(Inboxuser=current_user).order_by(Inbox.datetime.desc()).paginate(per_page=10, page=page)
    return render_template('inbox.html', mails=mails)


@app.route('/mail/outbox')
@login_required
def user_outbox():
    page = request.args.get('page', 1, type=int)
    mails = Outbox.query.filter_by(Outboxuser=current_user).order_by(Outbox.datetime.desc()).paginate(per_page=10, page=page)
    return render_template('outbox.html', mails=mails)

@app.route('/mail/inbox/view/<int:id>')
@login_required
def view_Inboxmail(id):
    if current_user == Inbox.query.get_or_404(id).Inboxuser:
        mail = Inbox.query.get_or_404(id)
        return render_template('view_Inboxmail.html', mail=mail)
    else:
        abort(403)

@app.route('/mail/outbox/view/<int:id>')
@login_required
def view_Outboxmail(id):
    if current_user == Outbox.query.get_or_404(id).Outboxuser:
        mail = Outbox.query.get_or_404(id)
        return render_template('view_Outboxmail.html', mail=mail)
    else:
        abort(403)

@app.route('/mail/inbox/delete/<int:id>')
@login_required
def Inboxmail_delete(id):
    if current_user == Inbox.query.get_or_404(id).Inboxuser:
        mail = Inbox.query.get_or_404(id)
        db.session.delete(mail)
        db.session.commit()
        flash("Deleted Successfully !", 'success')
        return redirect(url_for('user_inbox'))
    else:
        abort(403)

@app.route('/mail/outbox/delete/<int:id>')
@login_required
def Outboxmail_delete(id):
    if current_user == Outbox.query.get_or_404(id).Outboxuser:
        mail = Outbox.query.get_or_404(id)
        db.session.delete(mail)
        db.session.commit()
        flash("Deleted Successfully !", 'success')
        return redirect(url_for('user_outbox'))
    else:
        abort(403)

@app.route('/mail/draft')
@login_required
def user_draft():
    page = request.args.get('page', 1, type=int)
    mails = Draft.query.filter_by(Draftuser=current_user).order_by(Draft.datetime.desc()).paginate(per_page=10, page=page)
    return render_template('draft.html', mails=mails)

@app.route('/mail/draft/view/<int:id>')
@login_required
def view_Draftmail(id):
    if current_user == Draft.query.get_or_404(id).Draftuser:
        mail = Draft.query.get_or_404(id)
        return render_template('view_Draftmail.html', mail=mail)
    else:
        abort(403)

@app.route('/mail/draft/delete/<int:id>')
@login_required
def Draftmail_delete(id):
    if current_user == Draft.query.get_or_404(id).Draftuser:
        mail = Draft.query.get_or_404(id)
        db.session.delete(mail)
        db.session.commit()
        flash("Deleted Successfully !", 'success')
        return redirect(url_for('user_draft'))
    else:
        abort(403)

@app.route('/mail/draft/edit/<int:id>', methods=['GET','POST'])
@login_required
def Draftmail_edit(id):
    if current_user == Draft.query.get_or_404(id).Draftuser:
        form = Editdraft()
        draft = Draft.query.get_or_404(id)
        if form.validate_on_submit():
            draft.subject = form.subject.data
            draft.message = form.message.data
            draft.receiver = form.receiver.data
            db.session.commit()
            flash(f'Draft mail updated successfully.', 'success')
            return redirect(url_for('view_Draftmail', id=id))
        else:
            form.subject.data = draft.subject
            form.message.data = draft.message
            form.receiver.data = draft.receiver
            return render_template('edit_draft.html', form=form)
    else:
        abort(403)

@app.route('/mail/draft/send/<int:id>')
@login_required
def Draftmail_send(id):
    if current_user == Draft.query.get_or_404(id).Draftuser:
        mail = Draft.query.get_or_404(id)
        inbox = Inbox(subject=mail.subject, message=mail.message, sender=current_user.email)
        inbox.Inboxuser = User.query.filter_by(email=mail.receiver).first()
        db.session.add(inbox)

        outbox = Outbox(subject=mail.subject, message=mail.message, receiver=mail.receiver)
        outbox.Outboxuser = current_user
        db.session.add(outbox)
        db.session.commit()
        flash(f'Message sent successfully to {mail.receiver}', 'success')
        return redirect(url_for('user_outbox'))
    else:
        abort(403)

#error_handlers
@app.errorhandler(404)
def error_404(e):
    return render_template('error_404.html'), 404

@app.errorhandler(403)
def error_403(e):
    return render_template('error_403.html'), 403

@app.errorhandler(500)
def error_500(e):
    return render_template('error_500.html'), 500

