from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'elderly_help.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_AS_ASCII'] = False
    
    db.init_app(app)
    
    from app.routes import help_bp, stepcard_bp, stats_bp, user_bp, practice_bp, device_bp
    app.register_blueprint(help_bp, url_prefix='/api/help')
    app.register_blueprint(stepcard_bp, url_prefix='/api/stepcard')
    app.register_blueprint(stats_bp, url_prefix='/api/stats')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(practice_bp, url_prefix='/api/practice')
    app.register_blueprint(device_bp, url_prefix='/api/device')
    
    with app.app_context():
        db.create_all()
        from app.seed import seed_data
        seed_data()
    
    return app
