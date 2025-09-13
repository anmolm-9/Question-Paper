from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from config import Config
from routes.auth import auth_bp
from routes.user import user_bp
from routes.admin import admin_bp
from pathlib import Path

template_dir = Path(__file__).resolve().parent.parent / 'frontend'
print("Template Directory:", template_dir)
static_dir = template_dir
app = Flask(__name__, 
            template_folder=str(template_dir),
            static_folder=str(static_dir))

app.config.from_object(Config)
CORS(app, resources={r"/api/*": {"origins": Config.FRONTEND_URL}}, supports_credentials=True)

app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(user_bp, url_prefix="/api/user")
app.register_blueprint(admin_bp, url_prefix="/api/admin")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('auth/login.html')

@app.route('/register')
def register():
    return render_template('auth/register.html')

@app.route('/premium')
def premium():
    return render_template('auth/premium.html')

@app.route('/payment')
def payment():
    return render_template('auth/payment.html')

@app.route('/courses/<course>')
def course(course):
    course = course.split('.')[0] 
    return render_template(f'courses/{course}.html')

@app.route('/semester/<sem>')
def semester(sem):
    sem = sem.split('.')[0]
    return render_template(f'semester/{sem}.html')

@app.route('/admin')
def admin():
    return render_template('admin ui/admin.html')

@app.route('/year-paper/<path:paper>')
def year_paper(paper):
    print("Requested paper:", paper)
    paper = paper.split('.')[0]
    return render_template(f'year paper/{paper}.html')


@app.route('/subject-QP/<path:subject>')
def subject_qp(subject):
    print("Requested subject:", subject)
    subject = subject.split('.')[0]
    return render_template(f'subject QP/{subject}.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
