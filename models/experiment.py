from mongoengine import *

from core import BaseModel

class Experiment(BaseModel):

    # File where to save the measurements
    file = StringField(max_length=500)
    # Filters which the measurements should match. This is a finddict!
    filters = DictField(default = {})
    # Duration of the experiment
    since = DateTimeField()
    until = DateTimeField()
    active = BooleanField(default = True)

    def matches(self, measurement):
        """ See if this experiment matches a given measurement. """
        for k, v in self.filters.iteritems():
            if measurement.get(k) != v:
                return False
        return True

    @staticmethod
    def get_active_experiments():
        """ Get the active experiments in the database. """
        return Experiment.objects.filter(active = True)

    @staticmethod
    def get_experiments_matching(measurement):
        """ Get those experiments matching a given measurement. """
        return filter(lambda e: e.matches(measurement),
                      Experiment.objects.all())

