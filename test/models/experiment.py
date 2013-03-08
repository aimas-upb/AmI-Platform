from datetime import datetime
from unittest import TestCase

from mongoengine import connect
from nose.plugins.attrib import attr
from nose.tools import eq_, ok_

from models.experiment import Experiment

from core import settings

class ExperimentTestCase(TestCase):

    def setUp(self):
        super(ExperimentTestCase, self).setUp()
        connect('experiments')
        Experiment.objects.all().delete()

    @attr('unit')
    def test_save_and_fetch(self):
        """ Test that an experiment can be saved and fetched correctly. """

        connect('experiments', host=settings.MONGO_SERVER)

        e = Experiment(name='e1')
        e.since = datetime.now()
        e.until = datetime.now()
        e.file = 'file.txt'
        e.filters = {}
        e.name = 'test1'
        e.save()

        e2 = Experiment.objects.get(id = e.id)
        eq_(e2.file, e.file, "File of retrieved experiment should be equal")

    @attr('unit')
    def test_get_active_experiments_returns_active_experiment(self):
        connect('experiments')

        """ Test that get_active_experiments works correctly indeed. """
        e = Experiment(name = "e1", file = 'file2.txt', since = datetime.now())
        e.save()

        active = Experiment.get_active_experiments()
        eq_(active.count(), 1, "There should be exactly one active experiment")

        e.active = False
        e.save()
        active = Experiment.get_active_experiments()
        eq_(active.count(), 0, "There should be no active experiments")

    @attr('unit')
    def test_experiment_matches(self):
        e = Experiment(file = 'file3.txt', filters = {'a': 'b'}, name='test3')
        ok_(e.matches({'c': 'd', 'a': 'b'}))
        ok_(not e.matches({'c': 'd'}))
        ok_(not e.matches({'a': 'c'}))

    @attr('unit')
    def test_get_active_experiments_matching(self):
        connect('experiments')
        Experiment.objects.all().delete()

        e1 = Experiment(name = 'e1', file = 'file3.txt', filters = {'a': 'b'})
        e1.save()
        e2 = Experiment(name = 'e2', file = 'file3.txt', filters = {'c': 'd'})
        e2.save()

        matches = Experiment.get_active_experiments_matching({'a': 'b', 'c': 'd'})
        ok_(set(matches), set([e1, e2]))

        matches = Experiment.get_active_experiments_matching({'a': 'b'})
        ok_(set(matches), set([e1]))

        matches = Experiment.get_active_experiments_matching({'c': 'd'})
        ok_(set(matches), set([e2]))

        matches = Experiment.get_active_experiments_matching({'e': 'f'})
        eq_(len(matches), 0)

    @attr('unit')
    def test_inactive_matching_experiment_is_not_returned(self):
        connect('experiments')
        Experiment.objects.all().delete()
        e1 = Experiment(name = 'e1', file = 'file4.txt', filters = {'a': 'b'}, active=False)
        e1.save()

        matches = Experiment.get_active_experiments_matching({'a': 'b'})
        eq_(len(matches), 0)
