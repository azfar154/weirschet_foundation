from flask import Flask,render_template,flash,redirect,url_for,request
app = Flask(__name__)
import os
import secrets
from PIL import Image
from flask_bcrypt import Bcrypt
from forms import RegistrationForm,LoginForm,UpdateAccountForm,PostForm
from models import User,db,Post
from flask_login import login_user, current_user, logout_user, login_required
app.config['SECRET_KEY'] = '3tyyqty291757125ashfwqhvqjtvwq'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/newblog.db'
bcrypt = Bcrypt(app)
db.create_all()
from models import User
post= [
    {'name':'Jill',
    'place':'New Jersey',
    'allergies':'Peanuts'},
    {'name':'Jill',
    'place':'New York',
    'allergies' : 'None'
    }
]
@app.route("/")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html',people = posts)
@app.route('/register/',methods = ['GET','POST'])
def register():
    form = RegistrationForm()
    print(type(form))
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html',form = form)
@app.route("/login/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash("Login Successful!")
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)
@app.route('/about/')
def about():
    return render_template('about.html')
@app.route('/donate/')
def donate():
    return render_template('donate.html')
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)
@app.route("/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(location=form.location.data, allergies=form.allergies.data, name=current_user.username,user_id = current_user.id,contact=form.contact.data)
        print(form.location.data + " " + form.allergies.data + " " + str(current_user))
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')
if __name__ == "__main__":
    app.run(debug=True)