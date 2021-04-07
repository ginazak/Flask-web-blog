from datetime import datetime 
from blog import db
from blog import login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import re
from slugify import slugify

# https://learning.oreilly.com/library/view/learning-flask-framework/9781783983360/ch02s05.html#ch02lvl2sec29
def slugify(s):
    return re.sub('[^\w]+', '-', s).lower()


post_tags = db.Table('post_tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)


class Post(db.Model):

    id = db.Column(db.Integer,primary_key=True)
    date = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
    title = db.Column(db.Text,nullable=False)
    Description = db.Column(db.Text,nullable=False)
    content = db.Column(db.Text,nullable=False)
    image_file = db.Column(db.String(40),nullable=False,default='default.jpg')
    author_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    Category = db.Column(db.Text,nullable=False)

    user_likes = db.relationship('PostLike', backref='post', lazy='dynamic')
    tags = db.relationship('Tag', secondary=post_tags, backref=db.backref('posts', lazy='dynamic'))

    def __repr__(self):
        return f"Post('{self.date}','{self.title}','{self.content}')"




class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    password = db.Column(db.String(60), nullable=False)
    is_admin=db.Column(db.Boolean,nullable=False,default=False)
    
    post = db.relationship('Post', backref='user', lazy=True)
    comment=db.relationship('Comment',backref='user',lazy=True)
    post_likes = db.relationship('PostLike',foreign_keys='PostLike.user_id', backref='user', lazy='dynamic')

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def like_post(self, post):
        if not self.has_liked_post(post):
            like = PostLike(user_id=self.id, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(
                user_id=self.id,
                post_id=post.id).delete()

    def has_liked_post(self, post):
        return PostLike.query.filter(
            PostLike.user_id == self.id,
            PostLike.post_id == post.id).count() > 0

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


class PostLike(db.Model):
    __tablename__ = 'post_like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent = db.relationship('Comment', backref='comment_parent', remote_side=id, lazy=True)
    
    def __repr__(self):
        return f"Post('{self.date}', '{self.content}')"


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    slug = db.Column(db.String(64), unique=True)

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)
        self.slug = slugify(self.name)

    def __str__(self):
        return '<Tag %s>' % self.name