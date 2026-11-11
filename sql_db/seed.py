import click

from sql_db import sql_db, ph
from sql_db.models import *

def seed_users():
    # create dev user
    if not Users.query.filter_by(username="dev").first():
        # WARNING, THE PASSWORD IS JUST 'dev', DO NOT USE THIS IN PROD!!!
        dev = Users(username="dev", password=ph.hash("dev"))
        sql_db.session.add(dev)

def seed_groups():
    # create normal user group
    if not Groups.query.filter_by(group_name="user").first():
        user = Groups(group_name="user")
        sql_db.session.add(user)

    # create admin group
    if not Groups.query.filter_by(group_name="admin").first():
        admin = Groups(group_name="admin")
        sql_db.session.add(admin)

def seed_endpoints():
    # create /endpoints endpoint
    if not Endpoints.query.filter_by(endpoint_name="endpoints").first():
        endpoints = Endpoints(endpoint_name="endpoints")
        sql_db.session.add(endpoints)

    # create /token endpoint
    if not Endpoints.query.filter_by(endpoint_name="token").first():
        token = Endpoints(endpoint_name="token")
        sql_db.session.add(token)

def seed_permissions():
    # create admin permissions for /endpoints
    endpoints = Endpoints.query.filter_by(endpoint_name="endpoints").first()

    if not endpoints:
        raise Exception("Endpoint '/endpoints' does not exist.")
    
    if not Permissions.query.filter_by(permission_name="endpoints-admin").first():
        endpoints_admin = Permissions(
            epid=endpoints.epid,
            permission_name="endpoints-admin",
            mask=0b0100
        )
        sql_db.session.add(endpoints_admin)

    # create user permissions for /token
    token = Endpoints.query.filter_by(endpoint_name="token").first()

    if not token:
        raise Exception("Endpoint '/token' does not exist.")

    if not Permissions.query.filter_by(permission_name='token-user').first():
        token_user = Permissions(
            epid=token.epid,
            permission_name="token-user",
            mask=0b1101
        )
        sql_db.session.add(token_user)

def seed_group_users():
    # associate dev to user and admin
    dev = Users.query.filter_by(username="dev").first()
    user = Groups.query.filter_by(group_name="user").first()
    admin = Groups.query.filter_by(group_name="admin").first()

    if not dev:
        raise Exception("Could not find dev user")
    elif not user:
        raise Exception("Could not find user group")
    elif not admin:
        raise Exception("Could not find admin group")

    if not GroupUsers.query.filter_by(gid=user.gid, uid=dev.uid).first():
        user_dev = GroupUsers(gid=user.gid, uid=dev.uid)
        sql_db.session.add(user_dev)

    if not GroupUsers.query.filter_by(gid=admin.gid, uid=dev.uid).first():
        admin_dev = GroupUsers(gid=admin.gid, uid=dev.uid)
        sql_db.session.add(admin_dev)

def seed_group_permissions():
    # associate admin to endpoints-admin
    admin = Groups.query.filter_by(group_name="admin").first()
    endpoints_admin = Permissions.query.filter_by(permission_name="endpoints-admin").first()

    if not admin:
        raise Exception("Could not find admin group")
    elif not endpoints_admin:
        raise Exception("Could not find endpoints-admin permission")

    if not GroupPermissions.query.filter_by(gid=admin.gid, pmid=endpoints_admin.pmid).first():
        admin_endpoints_admin = GroupPermissions(gid=admin.gid, pmid=endpoints_admin.pmid)
        sql_db.session.add(admin_endpoints_admin)

    # associate user to token-user
    user = Groups.query.filter_by(group_name="user").first()
    token_user = Permissions.query.filter_by(permission_name="token-user").first()

    if not user:
        raise Exception("Could not find user group")
    elif not token_user:
        raise Exception("Could not find token-user permissions")

    if not GroupPermissions.query.filter_by(gid=user.gid, pmid=token_user.pmid).first():
        user_token_user = GroupPermissions(gid=user.gid, pmid=token_user.pmid)
        sql_db.session.add(user_token_user)


def seed_database():
    try:
        seed_users()
        seed_groups()
        seed_endpoints()
        seed_permissions()
        seed_group_users()
        seed_group_permissions()

        sql_db.session.commit()
    except Exception as e:
        print(f"seeding database failed: {e}")
        sql_db.session.rollback()
        raise


@click.command("seed")
def seed_command():
    seed_database()
    click.echo("Seeding database finished.")