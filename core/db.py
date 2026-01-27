import logging
from datetime import datetime

from django.conf import settings
from django.contrib.auth.hashers import make_password
from pymongo import MongoClient, ASCENDING

logger = logging.getLogger(__name__)

_client = None


def get_client():
    global _client
    if _client is None:
        if not settings.MONGO_URI:
            raise RuntimeError('MONGO_URI is not configured.')
        _client = MongoClient(settings.MONGO_URI)
    return _client


def get_db():
    client = get_client()
    return client[settings.MONGO_DB_NAME]


def get_collection(name):
    return get_db()[name]


def ping_mongo():
    try:
        client = get_client()
        client.admin.command('ping')
        logger.info('MongoDB ping successful.')
    except Exception as exc:
        logger.exception('MongoDB ping failed: %s', exc)
        raise RuntimeError('MongoDB is unreachable. Check MONGO_URI.') from exc


def ensure_indexes():
    db = get_db()
    db.users.create_index([('email', ASCENDING)], unique=True)
    db.signup_requests.create_index([('email', ASCENDING)], unique=True)
    db.employees.create_index([('employee_code', ASCENDING)], unique=True)
    db.salary_limits.create_index([('designation', ASCENDING)], unique=True)
    db.appraisals.create_index([('status', ASCENDING)])
    db.promotions.create_index([('status', ASCENDING)])


def ensure_maker_user():
    db = get_db()
    existing = db.users.find_one({'email': 'abhiyash@doggzi.com'})
    if existing:
        return
    db.users.insert_one(
        {
            'full_name': 'Abhiyash',
            'email': 'abhiyash@doggzi.com',
            'phone_number': '0000000000',
            'role': 'SUPERUSER',
            'status': 'ACTIVE',
            'password_hash': make_password('211310'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
    )
    logger.info('Seeded superuser abhiyash@doggzi.com')
