from fabric.api import task, local


@task
def deploy():
    local("heroku maintenance:on")
    local("git push heroku")
    local("heroku run alembic upgrade head")
    local("heroku maintenance:off")


@task
def swipe():
    local("heroku pgbackups:capture")
    local("curl -o latest.dump `heroku pgbackups:url`")
    local("pg_restore --verbose --clean --no-acl --no-owner " +
          "-d iati-datastore latest.dump")
