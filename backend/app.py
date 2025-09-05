from flask import Flask
from flask_cors import CORS
from database import init_db
from routes import user_routes, admin_routes
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_caching import Cache
from cachext import cache

migrate = Migrate() #for direct migrate imports

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'b6e7964b96adff617b7874b76be97027'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'another_super_secret'
    app.config['CACHE_TYPE'] = 'RedisCache'  ##redis for cacheing
    app.config['CACHE_REDIS_URL'] = 'redis://127.0.0.1:6379/3'
    
    cache.init_app(app)
    CORS(app, supports_credentials=True)
    JWTManager(app)
    init_db(app)
    
    
    # Register blueprints
    app.register_blueprint(user_routes)
    app.register_blueprint(admin_routes)
    
    return app




# Dev server start
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
