from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin


app = Flask(__name__)
app.config['SECRET_KEY'] = '<fce48146d3211b319f36b6bf8a2743e25ea05e6dba599c20>'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://c21014191:Virgogeek12!@csmysql.cs.cf.ac.uk:3306/c21014191_flasklabs'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)



from blog import routes
from blog.views import AdminView
from blog.models import User, Post, Comment, PostLike, Tag
admin = Admin(app,name='Admin panel',template_mode='bootstrap3')
admin.add_view(AdminView(User, db.session))
admin.add_view(AdminView(Post, db.session))
admin.add_view(AdminView(Comment, db.session))
admin.add_view(AdminView(Tag, db.session))
admin.add_view(AdminView(PostLike, db.session))