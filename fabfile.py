from fabric.api import task, local

@task
def deploy():
    local("heroku maintenance:on")
    local("git push heroku")
    local("heroku run alembic upgrade head")
    local("heroku maintenance:off")




