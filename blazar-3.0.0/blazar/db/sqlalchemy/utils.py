# -*- coding: utf-8 -*-
#
# Author: François Rossigneux <francois.rossigneux@inria.fr>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import datetime
import sys

import sqlalchemy as sa

from blazar.db.sqlalchemy import api
from blazar.db.sqlalchemy import facade_wrapper
from blazar.db.sqlalchemy import models
from blazar.manager import exceptions as mgr_exceptions
from blazar.plugins import instances as instance_plugin
from blazar.plugins import oshosts as host_plugin

get_session = facade_wrapper.get_session


def get_backend():
    """The backend is this module itself."""
    return sys.modules[__name__]


def _get_leases_from_resource_id(resource_id, start_date, end_date):
    session = get_session()
    border0 = sa.and_(models.Lease.start_date < start_date,
                      models.Lease.end_date < start_date)
    border1 = sa.and_(models.Lease.start_date > end_date,
                      models.Lease.end_date > end_date)
    query = (session.query(models.Lease).join(models.Reservation)
             .filter(models.Reservation.resource_id == resource_id)
             .filter(~sa.or_(border0, border1)))
    for lease in query:
        yield lease


def _get_leases_from_host_id(host_id, start_date, end_date):
    session = get_session()
    border0 = sa.and_(models.Lease.start_date < start_date,
                      models.Lease.end_date < start_date)
    border1 = sa.and_(models.Lease.start_date > end_date,
                      models.Lease.end_date > end_date)
    query = (session.query(models.Lease).join(models.Reservation)
             .join(models.ComputeHostAllocation)
             .filter(models.ComputeHostAllocation.compute_host_id == host_id)
             .filter(~sa.or_(border0, border1)))
    for lease in query:
        yield lease


def _get_leases_from_fip_id(fip_id, start_date, end_date):
    session = get_session()
    border0 = sa.and_(models.Lease.start_date < start_date,
                      models.Lease.end_date < start_date)
    border1 = sa.and_(models.Lease.start_date > end_date,
                      models.Lease.end_date > end_date)
    query = (session.query(models.Lease).join(models.Reservation)
             .join(models.FloatingIPAllocation)
             .filter(models.FloatingIPAllocation.floatingip_id == fip_id)
             .filter(~sa.or_(border0, border1)))
    for lease in query:
        yield lease


def get_reservations_by_host_id(host_id, start_date, end_date):
    session = get_session()
    border0 = sa.and_(models.Lease.start_date < start_date,
                      models.Lease.end_date < start_date)
    border1 = sa.and_(models.Lease.start_date > end_date,
                      models.Lease.end_date > end_date)
    query = (session.query(models.Reservation).join(models.Lease)
             .join(models.ComputeHostAllocation)
             .filter(models.ComputeHostAllocation.compute_host_id == host_id)
             .filter(~sa.or_(border0, border1)))
    return query.all()


def get_reservations_by_host_ids(host_ids, start_date, end_date):
    session = get_session()
    border0 = sa.and_(models.Lease.start_date < start_date,
                      models.Lease.end_date < start_date)
    border1 = sa.and_(models.Lease.start_date > end_date,
                      models.Lease.end_date > end_date)
    query = (session.query(models.Reservation).join(models.Lease)
             .join(models.ComputeHostAllocation)
             .filter(models.ComputeHostAllocation.compute_host_id
                     .in_(host_ids))
             .filter(~sa.or_(border0, border1)))
    return query.all()


def get_reservation_allocations_by_host_ids(host_ids, start_date, end_date,
                                            lease_id=None,
                                            reservation_id=None):
    session = get_session()
    border0 = models.Lease.end_date < start_date
    border1 = models.Lease.start_date > end_date
    query = (session.query(models.Reservation, models.ComputeHostAllocation)
             .join(models.Lease).join(models.ComputeHostAllocation)
             .filter(models.ComputeHostAllocation.compute_host_id
                     .in_(host_ids))
             .filter(~sa.or_(border0, border1)))
    if lease_id:
        query = query.filter(models.Reservation.lease_id == lease_id)
    if reservation_id:
        query = query.filter(models.Reservation.id == reservation_id)
    return query.all()


def get_plugin_reservation(resource_type, resource_id):
    if resource_type == host_plugin.RESOURCE_TYPE:
        return api.host_reservation_get(resource_id)
    elif resource_type == instance_plugin.RESOURCE_TYPE:
        return api.instance_reservation_get(resource_id)
    else:
        raise mgr_exceptions.UnsupportedResourceType(resource_type)


def get_free_periods(resource_id, start_date, end_date, duration,
                     resource_type='host'):
    """Returns a list of free periods."""
    reserved_periods = get_reserved_periods(resource_id,
                                            start_date,
                                            end_date,
                                            duration,
                                            resource_type=resource_type)
    free_periods = []
    previous = (start_date, start_date)
    if len(reserved_periods) >= 1:
        for period in reserved_periods:
            free_periods.append((previous[1], period[0]))
            previous = period
        free_periods.append((previous[1], end_date))
        if free_periods[0][0] == free_periods[0][1]:
            del free_periods[0]
        if free_periods[-1][0] == free_periods[-1][1]:
            del free_periods[-1]
    elif start_date != end_date and start_date + duration <= end_date:
        free_periods.append((start_date, end_date))
    return free_periods


def _get_events(resource_id, start_date, end_date, resource_type):
    """Create a list of events."""
    events = {}
    if resource_type == 'host':
        leases = _get_leases_from_host_id(resource_id, start_date, end_date)
    elif resource_type == 'floatingip':
        leases = _get_leases_from_fip_id(resource_id, start_date, end_date)
    else:
        mgr_exceptions.UnsupportedResourceType(resource_type)

    for lease in leases:
        if lease.start_date < start_date:
            min_date = start_date
        else:
            min_date = lease.start_date
        if lease.end_date > end_date:
            max_date = end_date
        else:
            max_date = lease.end_date
        if min_date in events.keys():
            events[min_date]['quantity'] += 1
        else:
            events[min_date] = {'quantity': 1}
        if max_date in events.keys():
            events[max_date]['quantity'] -= 1
        else:
            events[max_date] = {'quantity': -1}
    return events


def _find_reserved_periods(events, quantity, capacity):
    """Find the reserved periods."""
    reserved_periods = []
    used = 0
    reserved_start = None
    for event_date in sorted(events):
        used += events[event_date]['quantity']
        if not reserved_start and used + quantity > capacity:
            reserved_start = event_date
        elif reserved_start and used + quantity <= capacity:
            reserved_periods.append((reserved_start, event_date))
            reserved_start = None
    return reserved_periods


def _merge_periods(reserved_periods, start_date, end_date, duration):
    """Merge periods if the interval is too narrow."""
    reserved_start = None
    reserved_end = None
    previous = []
    merged_reserved_periods = []
    for period in reserved_periods:
        if not reserved_start:
            reserved_start = period[0]
        # Enough time between the two reserved periods
        if previous and period[0] - previous[1] >= duration:
            reserved_end = previous[1]
            merged_reserved_periods.append((reserved_start, reserved_end))
            reserved_start = period[0]
        reserved_end = period[1]
        previous = period
    if previous and end_date - previous[1] < duration:
        merged_reserved_periods.append((reserved_start, end_date))
    elif previous:
        merged_reserved_periods.append((reserved_start, previous[1]))
    if (len(merged_reserved_periods) >= 1 and
            merged_reserved_periods[0][0] - start_date < duration):
        merged_reserved_periods[0] = (start_date,
                                      merged_reserved_periods[0][1])
    return merged_reserved_periods


def get_reserved_periods(resource_id, start_date, end_date, duration,
                         resource_type='host'):
    """Returns a list of reserved periods for a resource.

    The get_reserved_periods function returns a list of periods during which
    the resource passed as parameter is reserved. The duration parameter
    allows to choose the minimum length of time for a period to be
    considered free.

    :param resource_id: the resource to consider
    :param start_date: start datetime of the entire period to consider
    :param end_date: end datetime of the entire period to consider
    :param duration: minimum length of time for a period to be considered free
    :param resource_type: A type of resource to consider
    :returns: the list of reserved periods for the resource, expressed as a
              list of two-element tuples, where the first element is the start
              datetime of the reserved period and the second is
              the end datetime
    """
    capacity = 1  # The resource status is binary (free or reserved)
    quantity = 1  # One reservation per host at the same time
    if end_date - start_date < duration:
        return [(start_date, end_date)]
    events = _get_events(resource_id, start_date, end_date, resource_type)
    reserved_periods = _find_reserved_periods(events, quantity, capacity)
    return _merge_periods(reserved_periods, start_date, end_date, duration)


def reservation_ratio(host_id, start_date, end_date):
    res_time = reservation_time(host_id, start_date, end_date).seconds
    return float(res_time) / (end_date - start_date).seconds


def availability_time(host_id, start_date, end_date):
    res_time = reservation_time(host_id, start_date, end_date)
    return end_date - start_date - res_time


def reservation_time(host_id, start_date, end_date):
    res_time = datetime.timedelta(0)
    for lease in _get_leases_from_host_id(host_id, start_date, end_date):
        res_time += lease.end_date - lease.start_date
        if lease.start_date < start_date:
            res_time -= start_date - lease.start_date
        if lease.end_date > end_date:
            res_time -= lease.end_date - end_date
    return res_time


def number_of_reservations(host_id, start_date, end_date):
    return sum(1 for x in
               _get_leases_from_host_id(host_id, start_date, end_date))


def longest_lease(host_id, start_date, end_date):
    max_duration = datetime.timedelta(0)
    longest_lease = None
    session = get_session()
    query = (session.query(models.Lease).join(models.Reservation)
             .join(models.ComputeHostAllocation)
             .filter(models.ComputeHostAllocation.compute_host_id == host_id)
             .filter(models.Lease.start_date >= start_date)
             .filter(models.Lease.end_date <= end_date))
    for lease in query:
        duration = lease.end_date - lease.start_date
        if max_duration < duration:
            max_duration = duration
            longest_lease = lease.id
    return longest_lease


def shortest_lease(host_id, start_date, end_date):
    # TODO(frossigneux) Fix max timedelta
    min_duration = datetime.timedelta(365 * 1000)
    longest_lease = None
    session = get_session()
    query = (session.query(models.Lease).join(models.Reservation)
             .join(models.ComputeHostAllocation)
             .filter(models.ComputeHostAllocation.compute_host_id == host_id)
             .filter(models.Lease.start_date >= start_date)
             .filter(models.Lease.end_date <= end_date))
    for lease in query:
        duration = lease.end_date - lease.start_date
        if min_duration > duration:
            min_duration = duration
            longest_lease = lease.id
    return longest_lease
