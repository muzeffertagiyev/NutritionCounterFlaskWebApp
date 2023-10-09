from flask import Flask, render_template, redirect, url_for , url_for, flash, request,session, abort

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship

from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import RegisterForm, LoginForm, AddDetailsForm, AddBirthdayForm, ChangeUsernameForm, ResetPasswordForm, BmiCalcForm, CalorieByActivitiesForm
from datetime import datetime

from nutrition import CalorieCounter

app = Flask(__name__)
app.config['SECRET_KEY'] = 'BYkEfBA6O6donzWlSihBXox7C0sKR6b'


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.context_processor
def global_variables():
    users = User.query.all()
    url=''
    if current_user.is_authenticated:
        url=url_for('user',username=current_user.username)
    else:
      url=url_for('home')

    return dict(users=users,url=url)

# LOGIN 
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.unauthorized_handler
def unauthorized():
    session['next_url'] = request.url
    # Redirect the user to the login page if they are not authenticated
    flash('You must be logged in first','danger')
    return redirect(url_for('login'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# FOR CALCULATING USER'S AGE
def calculate_age(form):
    day = int(form.birth_day.data)
    month = int(form.birth_month.data)
    year = int(form.birth_year.data)

    # Convert the month name to its numeric value
    birthdate = datetime(year, month, day)

    current_date = datetime.now()
    age = current_date.year - birthdate.year - ((current_date.month, current_date.day) < (birthdate.month, birthdate.day))

    return age

# CREATING DATA BASE
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///calorie_counter.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

with app.app_context():
    class User(UserMixin,db.Model):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(200), nullable=False, unique=True)
        email = db.Column(db.String(300), nullable=False, unique=True)
        password = db.Column(db.String(300), nullable=False)
        gender = db.Column(db.String(100),default='Unknown')
        weight = db.Column(db.String(100))
        height = db.Column(db.String(100))
        age = db.Column(db.String(100),default='Unknown')
        burned_calories = relationship("BurnedCalories", back_populates='user')

    class BurnedCalories(db.Model):
        __tablename__ = 'burned_calories'
        id = db.Column(db.Integer, primary_key=True)

        user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
        user = relationship("User", back_populates="burned_calories")

        date = db.Column(db.Date, default=datetime.now().date(), nullable=False)
        time = db.Column(db.String(8), default=datetime.now().strftime('%H:%M:%S'), nullable=False)
        exercise = db.Column(db.String(200), nullable=False)
        duration = db.Column(db.Float, nullable=False)
        calories = db.Column(db.Float, nullable=False)

    db.create_all()
    
# ---------------------------------------------------------------------------

# all Flask routes below
@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for('user',username=current_user.username))

    return render_template('index.html')


@app.route("/user/<username>/",methods=["GET"])
@login_required
def user(username):
    user = User.query.filter_by(username=username).first()
    
    page = request.args.get('page', 1, type=int)
    per_page = 15  # Number of exercises to display per page

    exercises = BurnedCalories.query.filter_by(user_id=user.id).order_by(BurnedCalories.id.desc()).paginate(page=page, per_page=per_page)

    if user is None:
        abort(404)  # Manually trigger a 404 error if the user doesn't exist

    return render_template('user.html',username=username,exercises=exercises)
    

@app.route('/register/', methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in. Please logout to Register a new account.', 'danger')
        return redirect(url_for('user',username=current_user.username))
    
    register_form = RegisterForm()

    
    if register_form.validate_on_submit():
        entered_email = register_form.email.data
        if User.query.filter_by(email=register_form.email.data.lower()).first():
            flash('You have already signed up with that email.Log in instead','danger')
            return redirect(url_for('login'))
        
        elif User.query.filter_by(username=register_form.username.data.lower()).first():
            flash('There is user with the same name. Please enter another name','danger')
            # return redirect(url_for('register'))
            register_form.email.data = entered_email

        else:

            hashed_and_salted_password = generate_password_hash(
                password=register_form.password.data, 
                method="pbkdf2:sha256",salt_length=8)

            new_user = User(
                username=register_form.username.data.lower(),
                email=register_form.email.data.lower(),
                password=hashed_and_salted_password
            )
            db.session.add(new_user)
            db.session.commit()

            session.clear()
            flash('Account was created ,now please add details and finish the registration','primary')
            login_user(new_user)
            return redirect(url_for('add_details'))


    return render_template("register.html",form=register_form)

@app.route('/login/', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in. Please logout to Login or to Register a new account.', 'danger')
        return redirect(url_for('user',username=current_user.username))
    login_form = LoginForm()

    if login_form.validate_on_submit():
        entered_email = login_form.email.data
        entered_password = login_form.password.data
        user = User.query.filter_by(email=entered_email).first()

        if not user :
            flash(f'That email does not exist,please try again Or Register','danger')
            return redirect(url_for('login'))

        elif not check_password_hash(pwhash=user.password, password=entered_password):
            flash('The password is incorrect,please try again','danger')
            login_form.email.data = entered_email
            
        else:
            login_user(user)
            next_url = session.get('next_url')
            if next_url:
                # Clear the stored next_url from the session
                session.pop('next_url', None)
                # Redirect the user back to the original URL
                return redirect(next_url)
            return redirect(url_for('user',username=current_user.username))
        
    return render_template("login.html", form=login_form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You logged out.You can login again','primary')
    return redirect(url_for('login'))

@app.route('/add_details/',methods=["POST","GET"])
@login_required
def add_details():
    user = current_user
    if user.gender and user.weight and user.height and user.age:
        flash('You have already filled out your details.Now you can update them only', 'danger')
        return redirect(url_for('profile', username=user.username))
    
    details_form = AddDetailsForm()
    birthday_form = AddBirthdayForm()

    if details_form.validate_on_submit() and birthday_form.validate_on_submit():
        user = current_user

        age = calculate_age(birthday_form)

        user.gender = details_form.gender.data
        user.weight = details_form.weight_kg.data.replace(',','.')
        user.height = details_form.height_cm.data
        user.age = age

        db.session.commit()

        return redirect(url_for('user',username=user.username))

    return render_template('add_details.html',form=details_form, birthday_form=birthday_form)


@app.route('/profile/<username>/')
@login_required
def profile(username):
    # prevent other users to enter others profile.
    user = User.query.filter_by(username=username).first_or_404()

    if user.id != current_user.id:
        flash("You can only access to your profile",'danger')
        return redirect(url_for('profile',username=current_user.username))
    
    return render_template('profile.html',user=user)

@app.route('/update_details/<username>/',methods=['POST',"GET"])
@login_required
def update_details(username):
    user = User.query.filter_by(username=username).first_or_404()
    details_form = AddDetailsForm()
    birthday_form = AddBirthdayForm()

    if current_user.id == user.id:
        if details_form.validate_on_submit():
        
            user.gender = details_form.gender.data
            user.weight = details_form.weight_kg.data.replace(',','.')
            user.height = details_form.height_cm.data

            db.session.commit()
            flash("Details were changed successfully",'success')
            return redirect(url_for('profile',username=username))
        
        details_form.weight_kg.data = user.weight
        details_form.height_cm.data = user.height
        
    else:
        flash("You can only edit Your Details",'danger')
        return redirect(url_for('profile',username=current_user.username))

    return render_template('add_details.html',form=details_form,birthday_form=birthday_form)

@app.route('/update_birthday/<username>/',methods=['POST',"GET"])
@login_required
def update_birthday(username):
    user = User.query.filter_by(username=username).first_or_404()
    birthday_form = AddBirthdayForm()
    details_form = AddDetailsForm()
    
    if current_user.id == user.id:
        if birthday_form.validate_on_submit():
            age = calculate_age(birthday_form)
            user.age = age

            db.session.commit()
            flash("Birthday was changed successfully",'success')
            return redirect(url_for('profile',username=username))
        
    else:
        flash("You can only edit Your Details",'danger')
        return redirect(url_for('profile',username=current_user.username))
    
    return render_template('add_details.html',birthday_form=birthday_form,form=details_form)

@app.route('/change_username/<username>/',methods=["GET","POST"])
@login_required
def change_username(username):
    user = User.query.filter_by(username=username).first_or_404()

    change_username_form = ChangeUsernameForm(obj=user)

    if current_user.id == user.id:
        if change_username_form.validate_on_submit():

            if User.query.filter_by(username=change_username_form.username.data.lower()).first():
                flash("This username already exists",'danger')
            
            else:
                user.username = change_username_form.username.data.lower()

                db.session.commit()
                flash('Your Details Were Updated Successfully','success')
                return redirect(url_for('profile',username=current_user.username))

    else:
        flash("You can only edit Your Details",'danger')
        return redirect(url_for('profile',username=current_user.username))
    
    return render_template('change_username.html', form=change_username_form)

@app.route('/reset_password/<username>/',methods=['GET','POST'])
@login_required
def reset_password(username):
    user = User.query.filter_by(username=username).first_or_404()
    reset_password_form = ResetPasswordForm()

    if current_user.id == user.id:

        if reset_password_form.validate_on_submit():
            old_entered_password = reset_password_form.old_password.data
            if not check_password_hash(pwhash=user.password, password=old_entered_password):
                flash('The old password is incorrect,please try again','danger')
                return redirect(url_for('reset_password',username=user.username))
            
            if old_entered_password == reset_password_form.new_password.data:
                flash("Please choose different new password from your old ones", 'danger')

            else:
                hashed_and_salted_password = generate_password_hash(
                    password=reset_password_form.new_password.data, 
                    method="pbkdf2:sha256",salt_length=8)
                
                user.password = hashed_and_salted_password

                db.session.commit()
                logout_user()
                flash('Your Password Was Reset Successfully. Please now Log In','success')
                return redirect(url_for('login'))

    else:
        flash("You can only Reset Your Password",'danger')
        return redirect(url_for('profile',username=current_user.username))
    
    return render_template('reset_password.html', form=reset_password_form)

@app.route('/delete/<int:user_id>/', methods=["GET", "POST"])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)
    
    if user:
        exercises = BurnedCalories.query.filter_by(user_id=user_id).all()
        
        if exercises:
            for exercise in exercises:
                db.session.delete(exercise)
        
        db.session.delete(user)
        db.session.commit()
        flash(f"User '{user.username}' and associated exercises were deleted successfully!", 'danger')
    else:
        flash(f"User not found.", 'danger')

    return redirect(url_for('home'))


bmi_categories = {
        'Underweight': (0, 18.4),
        'Healthy Weight': (18.5, 24.9),
        'Overweight': (25, 29.9),
        'Obesity': (30, float('inf'))
    }
@app.route('/bmi_body_calc/',methods=["GET","POST"])
def bmi_body_calc():

    user_bmi = ''
    user_result = ''
    # Check if the user is authenticated and has provided weight and height
    if current_user.is_authenticated:
        if current_user.weight and current_user.height:
            user_bmi = round(float(current_user.weight) / (int(current_user.height)/100)**2,1)
            for category, (lower, upper) in bmi_categories.items():
                if lower <= user_bmi <= upper:
                    user_result = category
                    break
        else:
            flash("Please add your details first",'info')
            return redirect(url_for('add_details'))

    form = BmiCalcForm()
    bmi=''
    result = ''
    if form.validate_on_submit():
        kg = float(form.weight_kg.data.replace(',','.'))    
        cm = int(form.height_cm.data)
        bmi = round(kg / ((cm/100)**2),1)

        # Determine the BMI category based on the calculated BMI
        for category, (lower, upper) in bmi_categories.items():
            if lower <= bmi <= upper:
                result = category
                break

     # Clear the form data
    form.weight_kg.data = ''
    form.height_cm.data = ''

    return render_template('bmi_body.html',form=form,bmi=bmi,result=result,user_bmi=user_bmi,user_result=user_result)

@app.route('/calorie_by_activities/',methods=['GET','POST'])
@login_required
def calorie_by_activities():
    calorie_form = CalorieByActivitiesForm()

    user = current_user

    gender = user.gender
    weight_kg = user.weight
    height_cm = user.height
    age = user.age


    if current_user.id == user.id:
        if current_user.weight and current_user.height:

            if calorie_form.validate_on_submit():
                data = CalorieCounter(gender,weight_kg,height_cm,age,calorie_form.query.data)
                nutrition_data = data.count()
                for exercise in nutrition_data:
                    title = exercise['name']
                    duration = exercise['duration_min']
                    calorie = exercise['nf_calories']

                    new_activity = BurnedCalories(
                        user_id = user.id,
                        exercise = title,
                        duration = duration,
                        calories = calorie
                    )

                    db.session.add(new_activity)
                    db.session.commit()
                flash("Activity was successfully added",'success')
                return redirect(url_for('user',username=current_user.username))

        else:
            flash("Please add your details first",'info')
            return redirect(url_for('add_details'))
    else:
        flash("You can only add activity in your account",'danger')
        return redirect(url_for('profile',username=current_user.username))

    return render_template('calorie_by_activities.html',form=calorie_form)

@app.route('/delete/')
@login_required
def delete_exercise():
    exercise_id = request.args.get('id')
    exercise = BurnedCalories.query.get(exercise_id)
    db.session.delete(exercise)
    db.session.commit()
    flash(f"Exercise '{exercise.exercise}' was deleted Successfully!",'danger')
    return redirect(url_for('user',username=current_user.username))

if __name__ == '__main__':
    app.run(debug=True)
