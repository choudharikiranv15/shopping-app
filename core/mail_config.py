from flask_mail import Mail
from flask import Flask

mail = Mail()


def init_mail(app: Flask):
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'workflexnetwork@gmail.com'
    app.config['MAIL_PASSWORD'] = 'tqey tfmd ftxl faol'
    app.config['MAIL_DEFAULT_SENDER'] = 'workflexnetwork@gmail.com'

    mail.init_app(app)
