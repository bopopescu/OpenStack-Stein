# Copyright 2014 Hewlett-Packard
# (C) Copyright 2015 Hewlett Packard Enterprise Development Company LP
# Copyright 2016 FUJITSU LIMITED
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from monasca_common.repositories.exceptions import AlreadyExistsException
from monasca_common.repositories.exceptions import DoesNotExistException
from monasca_common.repositories.exceptions import InvalidUpdateException
from monasca_common.repositories.exceptions import RepositoryException


class MultipleMetricsException(RepositoryException):
    pass


class UnsupportedDriverException(Exception):
    pass


__all__ = (
    'AlreadyExistsException',
    'DoesNotExistException',
    'InvalidUpdateException',
    'RepositoryException',
    'MultipleMetricsException',
    'UnsupportedDriverException'
)
