from flask import *
from study.forms import *
from study.db_models import *
from flask_login import login_required, current_user, login_user, logout_user
from study import *

def flash_message(message, category):
    flash(message, category)

# APP routes
def register_routes(app):
    @app.route('/')
    @app.route('/home')
    def home():
        return render_template('home.html')

    # Register Route
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            username = form.username.data
            email = form.email.data
            password = form.password.data

            existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
            if existing_user:
                flash_message('Username or email already exists. Please choose a different one.', 'danger')
                return render_template('register.html', form=form)

            new_user = User(username=username, email=email, password=password, confirmed=False)
            db.session.add(new_user)
            db.session.commit()
            send_confirmation_email(new_user.email)
            flash_message('A confirmation email has been sent via email. Please confirm your email to log in.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)
    
    # Email Confirmation Route
    @app.route('/confirm/<token>')
    def confirm_email(token):
        try:
            email = confirm_token(token)
        except:
            flash_message('The confirmation link is invalid or has expired.', 'danger')
            return redirect(url_for('resend_confirmation'))

        user = User.query.filter_by(email=email).first_or_404()
        if user.confirmed:
            flash_message('Account already confirmed. Please log in.', 'success')
        else:
            user.confirmed = True
            db.session.commit()
            flash_message('You have confirmed your account. Thanks!', 'success')
        return redirect(url_for('login'))
    
    # Re-send Confirmation Route
    @app.route('/resend_confirmation', methods=['GET', 'POST'])
    def resend_confirmation():
        form = ResendConfirmationForm()
        if form.validate_on_submit():
            email = form.email.data
            user = User.query.filter_by(email=email).first()
            if user and not user.confirmed:
                send_confirmation_email(user.email)
                flash_message('A new confirmation email has been sent.', 'success')
            else:
                flash_message('Email not found or already confirmed.', 'danger')
        return render_template('resend_confirmation.html', form=form)
    
    # Login Route
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            user = User.query.filter_by(username=username).first()
            if user and user.password == password:
                if not user.confirmed:
                    flash_message('Please confirm your email address first.', 'warning')
                    return redirect(url_for('resend_confirmation'))
                login_user(user)
                flash_message('User logged in successfully!', 'success')
                return redirect(url_for('dashboard' if user.profile else 'profile'))
            else:
                flash_message('Invalid username or password. Please try again.', 'danger')
                return render_template('login.html', form=form)
        return render_template('login.html', form=form)

    # Create Profile Route
    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        user = User.query.filter_by(username=current_user.username).first()
        if user.profile:
            return redirect(url_for('dashboard'))

        form = ProfileForm()
        if form.validate_on_submit():
            new_profile = Profile(
                username=user.username,
                school=form.school.data,
                primary_language=form.primary_language.data,
                secondary_languages=",".join(form.secondary_languages.data),
                days=",".join(form.days.data),
                times=",".join(form.times.data),
                strong_subjects=",".join(form.strong_subjects.data),
                weak_subjects=",".join(form.weak_subjects.data)
            )
            db.session.add(new_profile)
            db.session.commit()
            flash('Profile created successfully!', 'success')
            return redirect(url_for('dashboard'))
        return render_template('profile.html', form=form)
    
    # Update Profile Route
    @app.route('/profile/update', methods=['GET', 'POST'])
    @login_required
    def profileupdate():

        user = Profile.query.filter_by(username=current_user.username).first_or_404()
        form=ProfileForm(obj=user)

        if form.validate_on_submit():
            user.school = form.school.data
            user.primary_language = form.primary_language.data
            user.secondary_languages = ",".join(form.secondary_languages.data)
            user.days = ",".join(form.days.data)
            user.times = ",".join(form.times.data)
            user.strong_subjects = ",".join(form.strong_subjects.data)
            user.weak_subjects = ",".join(form.weak_subjects.data)
            db.session.commit()
            flash('Your profile has been updated!', 'success')
            return redirect(url_for('profile'))

        return render_template('updateprofile.html', form=form, user=user)
    
    # View Profile Route
    @app.route('/profile/view')
    @login_required
    def view_profile():
        user = Profile.query.filter_by(username=current_user.username).first_or_404()
        email = User.query.filter_by(username=current_user.username).first().email
        return render_template('view_profile.html', user=user, email=email)
    
    # Delete Profile Route
    @app.route('/profile/delete', methods=['GET','POST'])
    @login_required
    def delete_profile():
        user = User.query.filter_by(username=current_user.username).first_or_404()
        db.session.delete(user)
        db.session.commit()
        flash_message('Your profile has been deleted!', 'success')
        return redirect(url_for('home'))
    
    # Dashboard Route
    @app.route('/dashboard')
    @login_required
    def dashboard():
        user = User.query.filter_by(username=current_user.username).first_or_404()
        if not current_user.confirmed:
            flash_message('Please confirm your account!', 'warning')
            return redirect(url_for('resend_confirmation'))
        
        # Get groups the user is part of
        groups = Group.query.join(GroupMember).filter(GroupMember.user_id == user.username).all()

        #Get user profile
        user_profile = Profile.query.filter_by(username=current_user.username).first()
        strong_subjects = user_profile.strong_subjects.split(',') if user_profile and user_profile.strong_subjects else []
        weak_subjects = user_profile.weak_subjects.split(',') if user_profile and user_profile.weak_subjects else []
        return render_template('dashboard.html', user=user, groups=groups, user_profile=user_profile, strong_subjects=strong_subjects, weak_subjects=weak_subjects)
    
    # Logout Route
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash_message('Logged out successfully!', 'success')
        return redirect(url_for('home'))
    
    #See gruops
    @app.route('/group')
    @login_required
    def group():
        all_groups = Group.query.all()
        user_groups = Group.query.join(GroupMember).filter(GroupMember.user_id == current_user.username).all()
        return render_template('group.html', all_groups=all_groups, user_groups=user_groups)
    
    # Create Group Route
    @app.route('/group/new', methods=['GET', 'POST'])
    @login_required
    def create_group():
        form = CreateGroupForm()
        if form.validate_on_submit():
            new_group = Group(
                name=form.name.data,
                subject=form.subject.data,
                creator=current_user.username,
                days=",".join(form.days.data),
                times=",".join(form.times.data)
            )
            db.session.add(new_group)
            db.session.commit()

            # Add the creator as a member
            new_member = GroupMember(
                group_id=new_group.id,
                user_id=current_user.username
            )
            db.session.add(new_member)
            db.session.commit()
            flash_message('Group created successfully! You have been added as a member', 'success')
            return redirect(url_for('dashboard'))
        return render_template('create_group.html', form=form)
    
    # Join Group Route
    @app.route('/join_group/<int:group_id>')
    @login_required
    def join_group(group_id):
        # Handle joining the group
        group = Group.query.get_or_404(group_id)
        if group and len(group.members) < 10:
            # Add user to the group
            new_member = GroupMember(group_id=group.id, user_id=current_user.username)
            db.session.add(new_member)
            db.session.commit()
            flash_message('You have successfully joined the group!', 'success')
        else:
            flash_message('Group is full or does not exist.', 'danger')
        return redirect(url_for('group'))
    
    # Delete Group Route
    @app.route('/group/delete/<int:group_id>', methods=['GET','POST'])
    @login_required
    def delete_group(group_id):
        group = Group.query.get_or_404(group_id)
        if group.creator != current_user.username:
            flash_message('You are not authorized to delete this group.', 'danger')
            return redirect(url_for('group'))
        
        # Remove all members of the group
        GroupMember.query.filter_by(group_id=group_id).delete()
        db.session.delete(group)
        db.session.commit()
        flash_message('Group deleted successfully!', 'success')
        return redirect(url_for('group'))
    
    # Leave Group Route
    @app.route('/group/leave/<int:group_id>', methods=['GET','POST'])
    @login_required
    def leave_group(group_id):
        group = Group.query.get_or_404(group_id)
        
        # Check if the user is a member of the group
        membership = GroupMember.query.filter_by(group_id=group_id, user_id=current_user.username).first()
        if membership:
            db.session.delete(membership)
            db.session.commit()
            flash_message('You have left the group.', 'success')
        else:
            flash_message('You are not a member of this group.', 'danger')

        return redirect(url_for('group'))