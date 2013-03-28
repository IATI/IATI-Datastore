from . import AppTestCase
from . import factories as fac

from iatilib.model import Activity, Resource
from iatilib import db


class TestResource(AppTestCase):
    def test_replace_activities(self):
        # Activites are not updated in place. We only receive entire
        # docs (resources) which contain many actitivites, so to update
        # the db we remove all activites relating to a resource (plus
        # dependant objects) and replace them. These tests are me
        # working out how to do that in sqlalchemy.

        res = fac.ResourceFactory.create(
            activities=[fac.ActivityFactory.build(
                iati_identifier=u"t1",
                title=u"t1"
            )]
        )
        Activity.query.filter_by(resource_url=res.url).delete()
        # at this point res.activities has not been cleared
        res.activities = [
            fac.ActivityFactory.create(
                iati_identifier=u"t1",
                title=u"t2",
            )
        ]
        db.session.commit()
        self.assertEquals(res.activities[0].title, u"t2")
        self.assertEquals(
            Resource.query.get(res.url).activities[0].title, u"t2")
