import os 

from pathlib import Path


class BaseConfig(object):
    VERSION = "0.1.0"
    MINIFY = False

    SECRET_KEY = 'qt584635@(*$(KC=oijr )*@$*^SAd- okasfoijh*(@Y$*)A)S(+D' # move this to os.environment

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

    UPLOAD_FOLDER = Path(__file__).parent.parent / 'uploads'

    ACTIVE_APPS = (
        "blog",
        "ecommerce"
    )

    CACHE_TYPE = 'simple'

    # MAIL_SERVER = ""
    # MAIL_USERNAME = ""
    # MAIL_PASSWORD = ""

    # ADMIN_EMAIL = ""

    # MAIL_SUBJECT_PREFIX = '[]'
    # MAIL_SENDER = 'Info <@.com>'


    # ZARINPAL_MERCHANT_ID = ''
    # ZARINPAL_WEBSERVICE = ''

    # RECAPTCHA_ENABLED = True
    # RECAPTCHA_SITE_KEY = ""
    # RECAPTCHA_SECRET_KEY = ""
    # RECAPTCHA_THEME = "light"
    # RECAPTCHA_TYPE = "image"
    # RECAPTCHA_SIZE = "compact"
    # RECAPTCHA_RTABINDEX = 10


class DevConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'postgresql://dev_shop:123@localhost/dev_shop'
    DEBUG = True


class ProdConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'postgresql://dev_shop:123@localhost/dev_shop'
    DEBUG = False