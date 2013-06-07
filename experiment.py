#!/usr/bin/python

import argparse
from datetime import datetime
import json
import logging
import os
import sys

from mongoengine import connect
from mongoengine.queryset import MultipleObjectsReturned, DoesNotExist
import kestrel

from core.measurements_player import MeasurementsPlayer
from core import settings
from lib.log import setup_logging

def we_are_frozen():
    # All of the modules are built-in to the interpreter, e.g., by py2exe
    return hasattr(sys, "frozen")

def module_path():
    encoding = sys.getfilesystemencoding()
    if we_are_frozen():
        return os.path.dirname(unicode(sys.executable, encoding))
    return os.path.dirname(unicode(__file__, encoding))

from models.experiment import Experiment

logger = logging.getLogger(__name__)
setup_logging()

parser = argparse.ArgumentParser(description='Manage experiments')
parser.add_argument('--file',
                    default='experiment.exp',
                    help='File in which to dump the measurements')
parser.add_argument('--filters',
                    default='{}',
                    help='Key-value filters for measurements')
parser.add_argument('operation',
                    help='Operation to perform (start/stop)')
parser.add_argument('name',
                    help='Experiment name')

args = parser.parse_args()

if args.operation not in ['start', 'stop', 'delete', 'play']:
    logger.error("Invalid operation: %s" % args.operation)

elif args.operation == 'start':
    # See if there is an existing Experiment with that name
    try:
        connect('experiments', host=settings.MONGO_SERVER)
        e = Experiment.objects.get(name=args.name)
        logger.error("There is already an experiment with the name %s!" %
                     args.name)
    except DoesNotExist:
        e = Experiment(name=args.name,
                       filters=json.loads(args.filters),
                       file=args.file,
                       since=datetime.now(),
                       active=True)
        e.save()
    except MultipleObjectsReturned:
        logger.error("There is more than one experiment with name %s! "
                     "Database is corrupted." % args.name)

elif args.operation == 'stop':
    try:
        connect('experiments', host=settings.MONGO_SERVER)
        e = Experiment.objects.get(name=args.name)
        if not e.active:
            logger.error("The experiment %s is not active!" % args.name)
        else:
            e.active = False
            e.save()
    except DoesNotExist:
        logger.error("There is no experiment with name %s!" % args.name)

elif args.operation == 'delete':
    try:
        connect('experiments', host=settings.MONGO_SERVER)
        e = Experiment.objects.get(name=args.name)
        e.delete(safe=True)
    except DoesNotExist:
        logger.error("There is no experiment with name %s!" % args.name)

elif args.operation == 'play':
    try:
        connect('experiments', host=settings.MONGO_SERVER)
        file_name = Experiment.objects.get(name=args.name).file
        connection = kestrel.Client(settings.KESTREL_SERVERS)
        f = lambda m: connection.add('measurements', m)
        player = MeasurementsPlayer(data_file=file_name,
                                    callback=f)
        player.play()
    except DoesNotExist:
        logger.error("There is no experiment with name %s!" % args.name)
