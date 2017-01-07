class DevelopmentConfig(object):
    DATABASE_URI = "postgresql://ubuntu:thinkful@localhost:5432/barbuddy"
    DEBUG = True

class TestingConfig(object):
    DATABASE_URI = "postgresql://ubuntu:thinkful@localhost:5432/barbuddy-test"
    DEBUG = True
