from sql_db import sql_db
from sql_db.models import *

# retrieves user uid's permissions for endpoint epid
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