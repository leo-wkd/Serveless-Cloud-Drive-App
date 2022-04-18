class Config(object):
    ACCESS_KEY = "AKIA2YDCPYNJFV3KUWEJ"
    ACCESS_SECRET = "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"
    # ACCESS_KEY = "AKIA6LMAN5HVJ4ZQPVYU"
    # ACCESS_SECRET = "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"
    BUCKET_NAME = "ece1779cc"
    ZONE = "us-east-1"
    JSON_SORT_KEYS = False
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    # SQLALCHEMY_DATABASE_URI = "mysql://admin:wty19980711@ece1779.cpyauwicojwb.us-east-1.rds.amazonaws.com/webapp_2"
    SQLALCHEMY_DATABASE_URI = 'mysql://admin:19971121@ece1779-a2.cdq1cmhoazdn.us-east-1.rds.amazonaws.com:3306/webapp_2'
    SQLALCHEMY_TRACK_MODIFICATIONS = True