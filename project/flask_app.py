from flask import Flask
from flask import render_template

def create_app():
    app = Flask(__name__)
    
    from route.part3 import part3
    app.register_blueprint(part3)

    @app.route('/')
    def main_index():
        return render_template('index.html')

    return app

if __name__ == "__main__" :
    app = create_app()
    app.run()