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

def seed_permissions():
    # create admin permissions for /endpoints
    endpoint = Endpoints.query.filter_by(endpoint_name="endpoints").first()

    if not endpoint:
        raise Exception("Endpoint '/endpoints' does not exist.")
    
    if not Permissions.query.filter_by(permission_name="endpoints-admin").first():
        endpoints_admin = Permissions(
            epid=endpoint.epid,
            permission_name="endpoints-admin",
            mask=0b0100
        )
        sql_db.session.add(endpoints_admin)

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
    
def seed_test_user():
    if not Users.query.filter_by(username="test_user").first():
        pass

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