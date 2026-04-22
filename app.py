from flask import Flask, render_template
from models.db import init_db
from routes.novel_routes import novels_bp
from routes.analysis_routes import analysis_bp
from routes.process_routes import process_bp
from routes.admin_routes import admin_bp
from config.settings import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_blueprint(novels_bp, url_prefix='/api')
    app.register_blueprint(analysis_bp, url_prefix='/api')
    app.register_blueprint(process_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/analysis')
    def analysis():
        return render_template('analysis.html')

    @app.route('/admin')
    def admin():
        return render_template('admin.html')

    return app


if __name__ == '__main__':
    app = create_app()
    try:
        init_db()
    except Exception as e:
        print(f"Database init warning: {e}")
    app.run(host='0.0.0.0', port=5001, debug=True)