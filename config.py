import os

PART_CUSTOM_FIELDS = [
    'parent_assembly',
    'file_type',
    'type',
    'sets',
    'to_order',
]
PART_DIAGNOSTICS_FIELDS = [
    'parent',
    'child',
    'is_production',
    'is_fastener',
    'is_purchased',
    'is_junk',
    'is_junk_by_flag_keys',
    'is_junk_by_empty_fields',
    'is_junk_by_purchased_part_nesting',
]


class BaseConfig(object):
    """Base config"""
    TESTING = False
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    IMPORTS_FOLDER = './web_app/assets/imports/'
    EXPORTS_FOLDER = './web_app/assets/exports/'
    ALLOWED_EXTENSIONS = {'csv'}
    SESSION_TYPE = 'filesystem'
    PART_ADDITIONAL_FIELDS = PART_CUSTOM_FIELDS

    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True


class ProductionConfig(BaseConfig):
    """Uses production database server."""


class DevelopmentConfig(BaseConfig):
    PART_ADDITIONAL_FIELDS = PART_CUSTOM_FIELDS + PART_DIAGNOSTICS_FIELDS


class TestingConfig(BaseConfig):
    TESTING = True


config = {
    'development': DevelopmentConfig,
    'test': TestingConfig,
    'production': ProductionConfig
}
