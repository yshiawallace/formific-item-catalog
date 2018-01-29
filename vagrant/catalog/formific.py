from flask import Flask
from database import init_db
import error_handlers
from auth.controller import auth
from views.controller import views


init_db()

app = Flask(__name__)

# Register blueprints
app.register_blueprint(error_handlers.blueprint)
app.register_blueprint(auth)
app.register_blueprint(views)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
