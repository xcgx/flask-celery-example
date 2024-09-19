from app import celery, app
from flask_mail import Mail, Message
import random
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mail = Mail(app)

@celery.task
def send_async_email(email_data):
    """Background task to send an email with Flask-Mail."""
    logger.info("Sending async email to %s", email_data['to'])
    msg = Message(email_data['subject'],
                  sender=email_data.get('sender', app.config['MAIL_DEFAULT_SENDER']),
                  recipients=[email_data['to']])
    msg.body = email_data['body']
    mail.send(msg)
    logger.info("Email sent to %s", email_data['to'])

@celery.task(bind=True)
def long_task(self):
    """Background task that runs a long function with progress reports."""
    logger.info('Starting long task')
    try:
        verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
        adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
        noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
        message = ''
        total = random.randint(10, 50)
        logger.info(f'Total steps: {total}')
        for i in range(total):
            if not message or random.random() < 0.25:
                message = f'{random.choice(verb)} {random.choice(adjective)} {random.choice(noun)}...'
            self.update_state(state='PROGRESS',
                              meta={'current': i, 'total': total, 'status': message})
            logger.info(f'Progress: {i}/{total} - {message}')
            time.sleep(1)
        logger.info('Task completed')
        return {'current': 100, 'total': 100, 'status': 'Task completed!', 'result': 42}
    except Exception as e:
        logger.error(f'Task failed: {str(e)}')
        self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e)})
        raise
