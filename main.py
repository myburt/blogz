from flask import Flask, request, redirect, render_template, session,flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:SmallWord@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = "m~kmSUK>:(j0f)4|wbP(.&CLZ6XWGU"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))    

    def __init__(self, title, content, owner_id):
        self.title = title
        self.content = content
        self.owner_id = owner_id
        
class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(32))
    blogs = db.relationship('Blog', backref='owner')

    def __init___(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'list_blogs', 'index']
    if request.endpoint not in allowed_routes and 'the_user' not in session:
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html',title="Build-a-Blog!")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['the_user'] = username
            flash("Logged in", "info")
            return redirect('/newpost')
        elif user == None:
            flash("username does not exist", "error")
        else:
            flash('User password incorrect', 'error')

    return render_template('login.html')

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        #get form data
        username = request.form["username"]
        password = request.form["password"]
        verify_pass = request.form["verify"]

        #check to see if there is already a user with "username" in db
        existing_user = User.query.filter_by(username=username).first()

        #flag for determining if errors happen
        has_errors = False
        
        if not username or not password or not verify_pass:
            flash("please make sure all fields have been filed out.","error")
            has_errors = True
        if password and not(password == verify_pass):
            flash("Password and verify password do not match","error")
            has_errors = True
        if password and len(password) < 3:
            flash("Your password must be at least 3 characters long no more than 32", "error")
            has_errors = True
        if username and len(username) < 3:
            flash("Your username must be at least 3 characters long no more than 32", "error")
            has_errors = True
        if existing_user:
            flash("An account with this username already exists do you want to <a href=/login>Login</a>" , "error")
            has_errors = True

        if has_errors:
            return render_template("signup.html", username=username)
            
        if not existing_user:
            new_user = User(username = username, password = password)
            db.session.add(new_user)
            db.session.commit()
            session['the_user'] = username
            return redirect('/')

    else:
        return render_template("signup.html")
        
@app.route('/logout', methods=["GET"])
def logout():
    del session["the_user"]
    return redirect('/')

@app.route('/blog', methods=['GET', 'POST'])
def blog_list():
    returned_id = request.args.get('blog_id')

    if returned_id:
        blog_to_view = Blog.query.get(returned_id)
        
        return render_template('blog.html', title=blog_to_view.title, blog_view = blog_to_view)

    if request.method == 'POST':
        task_name = request.form['task']
        new_task = Task(task_name)
        db.session.add(new_task)
        db.session.commit()

    blogs = Blog.query.all()

    return render_template('blog.html',title="Build-a-Blog!", blogs=blogs, in_session=True)

@app.route('/newpost', methods=['GET', 'POST'])
def add_blog():

    if request.method == 'POST':
        blog_name = request.form['blog-name']
        blog_message = request.form['blog-message']
        errror_title = ""
        error_content = ""

        if blog_name == "":
            errror_title = "You must have a title for your blog"
        if blog_message == "":
            error_content = "Please add some words of wisdom to your blog post."

        if errror_title or error_content:
            return render_template('newpost.html', title="Add a Blog", error_title = errror_title, error_content = error_content,
                                    blog_name = blog_name ,blog_message = blog_message, in_session=True)

        blog_entry = Blog(blog_name, blog_message)

        db.session.add(blog_entry)
        db.session.commit()

        return redirect('/blog?blog_id=' + str(blog_entry.id))

    else:
        return render_template('newpost.html',title="Add a Blog", in_session=True)

    


if __name__ == '__main__':
    app.run()