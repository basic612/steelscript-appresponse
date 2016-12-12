# Copyright (c) 2016 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.

import logging

from steelscript.common import timeutils

logger = logging.getLogger(__name__)


class InvalidType(Exception):
    pass


class ServiceClass(object):
    """Service classes are implemented as descriptors:
    They are not fully fledged service objects until
    they are called second time. 'common' service is
    an exception because it will always be used to fetch
    service versions first."""

    initialized = False

    def _bind_resources(self):
        pass

    def __get__(self, obj, objtype):
        if self.initialized:
            return self

        self.initialized = True

        logger.debug('initializing %s service' % self.__class__.__name__)
        self._bind_resources()
        return self


# This class is used for instance descriptors
# http://blog.brianbeck.com/post/74086029/instance-descriptors
class InstanceDescriptorMixin(object):

    def __getattribute__(self, name):
        value = object.__getattribute__(self, name)
        if hasattr(value, '__get__'):
            value = value.__get__(self, self.__class__)
        return value


class Column(object):

    def __init__(self, name, key=False):
        self.name = name
        self.key = key

    def __str__(self):
        return self.name


class Key(Column):

    def __init__(self, name):
        super(Key, self).__init__(name, key=True)


class Value(Column):

    def __init__(self, name):
        super(Value, self).__init__(name, key=False)


class TimeFilter(object):

    def __init__(self, duration=None, start=None, end=None):
        """Initialize a TimeFilter object.

         :param start integer: start time in epoch seconds
         :param end integer: end time in epoch seconds
         :param duration string: time duration, i.e. '1 hour' or 'last 1 hour'

        """

        if start and end:
            self.start = str(start)
            self.end = str(end)

        elif not start and not end:
            start, end = timeutils.parse_range(duration)
            self.start = start.strftime('%s')
            self.end = end.strftime('%s')

        else:
            td = timeutils.parse_timedelta(duration).total_seconds()
            if start:
                self.start = str(start)
                self.end = str(int(start + td))
            else:
                self.start = str(int(end - td))
                self.end = str(end)