from flask import Flask, render_template, url_for, request, redirect, flash, g
from blog import app, db
from blog.models import User, Post, Comment, PostLike, Tag
from blog.forms import RegistrationForm, ContactForm, LoginForm, CommentForm,TagForm, TagField
from flask_login import login_user, login_required, current_user, logout_user
from sqlalchemy import desc, asc

@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.filter(Post.Category=='Academic')
    return render_template('home.html', title='Home', posts = posts)


@app.route("/about/<sort_by>")
def about(sort_by):
    value = request.args.get('sort_by','')
    page = request.args.get('page', 1, type=int)
    if sort_by == 'asc':
        posts = Post.query.order_by(Post.date.asc()).paginate(page=page, per_page=4)
    if sort_by == 'desc':
        posts = Post.query.order_by(Post.date.desc()).paginate(page=page, per_page=4)
    next_url = url_for('about', sort_by=sort_by, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('about',sort_by=sort_by, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('about.html',posts=posts, title='All Posts',sort_by=sort_by, next_url=next_url, prev_url=prev_url)


@app.route("/settings")
@login_required
def settings():
    pass

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter(Comment.post_id == post.id)
    form = CommentForm()
    return render_template('post.html', post=post, comments=comments, form=form)

@app.route('/post/<int:post_id>/comment', methods=['GET', 'POST'])
@login_required
def post_comment(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        db.session.add(Comment(content=form.comment.data, post_id=post.id, author_id=current_user.id))
        db.session.commit()
        flash("Your comment has been added to the post", "success")
        return redirect(f'/post/{post.id}')
    comments = Comment.query.filter(Comment.post_id == post.id)
    return render_template('post.html', post=post, comments=comments,form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Thank you for registering!Log in for more..')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            flash('Great! You\'re in!')
            return redirect(url_for('home'))
        else:
            flash(u'Invalid email address or password', 'error')
            return render_template('login.html',form=form)
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/contact",methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if request.method == 'POST':
        name =  request.form["name"]
        email = request.form["email"]
        message = request.form["message"]
        res = pd.DataFrame({'name':name, 'email':email, 'subject':subject ,'message':message}, index=[0])
        res.to_csv('./contactusMessage.csv')
        print("The data is saved !")
    else:
        return render_template('contact.html', form=form)


@app.route("/success")
def success():
    return render_template('success.html', title='success')


@app.login_manager.unauthorized_handler
def unauth_handler():
    return jsonify(success=False,
                   data={'login_required': True},
                   message='Authorize please to access this page'), 401


@app.route('/like_action2/ <int:post_id>/ <action>')
@login_required
def like_action2(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
    return redirect(request.referrer)


# Code to build searching system adapted from 
# Learning Flask Framework e-book by OReilly
# accessed 25-2-2021 
# https://learning.oreilly.com/library/view/learning-flask-framework/9781783983360/ch03s03.html

def object_list(template_name, query, paginate_by=20, **context):
    page = request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1
    object_list = query.paginate(page, paginate_by)
    return render_template(template_name, object_list=object_list,
    **context)


def search_list(template, query, **context):
    search = request.args.get('q')
    if search:
        query = query.filter(
            (Post.content.contains(search))|
            (Post.title.contains(search))|
            (Post.author_id.contains(search)))
    return object_list(template, query, **context)



@app.route("/search")
def search_index():
    entries = Post.query.order_by(Post.date.desc())
    return search_list('search.html', entries)


@app.route('/tag_post2/', methods=['GET', 'POST'])
@login_required
def tag_post2():
    if request.method == 'POST':
        form = TagForm(request.form)
        tag = form.save_tag(Tag())
        db.session.add(tag)
        db.session.commit()
        return redirect(url_for('tag_index', slug=tag.slug))
    else:
        form = TagForm()
    return render_template('post.html', form=form)


@app.route("/alltags")
def tag_index():
    tags = Tag.query.order_by(Tag.name).all()
    return render_template('tag_index.html', title = "alltags", tags=tags)


@app.route('/tags/<int:post_id>/')
def tag_detail(post_id):
    tag = Tag.query.filter(Tag.id == post_id).first_or_404()
    posts = tag.posts.order_by(Post.date.desc())
    return render_template('tag_detail.html',posts=posts,tag=tag)



