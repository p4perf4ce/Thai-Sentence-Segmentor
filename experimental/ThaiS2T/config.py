import os
# You need to replace the next values with 
# the appropriate values for your configuration

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"

# Upload Handler

STORAGE = 'storage/'
# UPLOAD_TO_S3 = True
S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
#AWS_AC_KEYID = os.environ.get('AWS_ACCESS_KEY_ID')
#AWS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
# OVERRIDE KEY (Development Only)
S3_BUCKET = 'thtranscribe-bucket'

ALLOWED_VIDEO_EXTENSION = set(['mp4', 'mkv', 'wmv', 'avi', 'flac', 'mp3'])

DEBUG = True
# APP Handler

ALLOW_OVERWRITE = True
ENABLE_MULTIPROCESS_REQUEST = True
WRITE_AUDIO2DISK = True
PROHIBIT_SAVEPATH = [
                        '/', '/root', '/lib', '/boot',
                        '/lib64', '/opt', '/bin', '/usr'
                    ]

MAX_SIMU_OUTBOUND_REQUEST = 16

# Celery Worker Conf

TASK_TRACK_START = True
REDIS_URL = os.environ.get('REDIS_URL', 'redis:///')
BACKEND_URL = os.environ.get('REDIS_URL', 'redis://')
# Overwrite Heroku Config Vars (If needed to use absolute url)
# BACKEND_URL = REDIS_URL


# Transcribe Config
GOOGLE_OAUTH2_CREDS_PATH = './ThaiS2T/credentials/credkey.json'
DEFAULT_META_DIR = '/metadata/'
DEFAULT_TRANS_DIR = '/text/'
DEFAULT_TRANS_NAME = 'subtitle.srt'