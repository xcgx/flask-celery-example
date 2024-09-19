import os
from flask import Flask, request, render_template, session, flash, redirect, url_for, jsonify
from flask_mail import Mail
from celery import Celery

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY']['broker_url'])
    celery.conf.update(app.config['CELERY'])
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'

# Flask-Mail configuration
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_password'
app.config['MAIL_DEFAULT_SENDER'] = 'flask@example.com'

# Celery configuration
app.config.update(
    CELERY=dict(
        broker_url='redis://127.0.0.1:6379/0',
        result_backend='redis://127.0.0.1:6379/0',
        task_serializer='json',
        result_serializer='json',
        accept_content=['json'],
        timezone='UTC',
        enable_utc=True,
    )
)

# Initialize extensions
mail = Mail(app)

# Initialize Celery
celery = make_celery(app)

# Import tasks to register them with Celery
import tasks

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', email=session.get('email', ''))
    email = request.form['email']
    session['email'] = email

    email_data = {
        'subject': 'Hello from Flask',
        'to': email,
        'body': 'This is a test email sent from a background Celery task.'
    }
    if request.form['submit'] == 'Send':
        tasks.send_async_email.delay(email_data)
        flash(f'Sending email to {email}')
    else:
        tasks.send_async_email.apply_async(args=[email_data], countdown=60)
        flash(f'An email will be sent to {email} in one minute')

    return redirect(url_for('index'))

@app.route('/longtask', methods=['POST'])
def longtask():
    task = tasks.long_task.apply_async()
    return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = tasks.long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {'state': task.state, 'current': 0, 'total': 1, 'status': 'Pending...'}
    elif task.state != 'FAILURE':
        response = {'state': task.state, 'current': task.info.get('current', 0), 'total': task.info.get('total', 1), 'status': task.info.get('status', '')}
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        response = {'state': task.state, 'current': 1, 'total': 1, 'status': str(task.info)}
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
