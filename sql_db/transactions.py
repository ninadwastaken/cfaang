from functools import wraps
from sqlalchemy import text

from sql_db import sql_db
from sql_db.models import *

# small check to see sql_db is reachable
def requires_db(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            sql_db.session.execute(text("SELECT 1"))
        except Exception as e:
            sql_db.session.rollback()
            print(f"MariaDB could not be reached: {e}")
            raise

        return fn(*args, **kwargs)

    return wrapper

# retrieves user uid's permissions for endpoint epid
@requires_db
def get_user_permissions(uid, epid):
    return sql_db.session.query(
        sql_db.func.coalesce(
            sql_db.func.bit_or(Permissions.mask), 0
        )
    ).join(
        GroupPermissions,
        Permissions.pmid == GroupPermissions.pmid
    ).join(
        GroupUsers,
        GroupPermissions.gid == GroupUsers.gid
    ).filter(
        GroupUsers.uid == uid,
        Permissions.epid == epid
    ).scalar()