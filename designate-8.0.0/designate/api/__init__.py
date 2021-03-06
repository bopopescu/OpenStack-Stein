# Copyright 2012 Managed I.T.
#
# Author: Kiall Mac Innes <kiall@managedit.ie>
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
from oslo_config import cfg


api_group = cfg.OptGroup(
    name='service:api', title="Configuration for API Service"
)

api_opts = [
    cfg.IntOpt('workers',
               help='Number of api worker processes to spawn'),
    cfg.IntOpt('threads', default=1000,
               help='Number of api greenthreads to spawn'),
    cfg.BoolOpt('enable-host-header', default=False,
               help='Enable host request headers'),
    cfg.StrOpt('api-base-uri', default='http://127.0.0.1:9001/',
               help='the url used as the base for all API responses,'
                    'This should consist of the scheme (http/https),'
                    'the hostname, port, and any paths that are added'
                    'to the base of Designate is URLs,'
                    'For example http://dns.openstack.example.com/dns'),
    cfg.IPOpt('api_host',
              deprecated_for_removal=True,
              deprecated_reason="Replaced by 'listen' option",
              help='API Bind Host'),
    cfg.PortOpt('api_port',
                deprecated_for_removal=True,
                deprecated_reason="Replaced by 'listen' option",
                help='API Port Number'),
    cfg.ListOpt('listen',
                default=['0.0.0.0:9001'],
                help='API host:port pairs to listen on'),
    cfg.StrOpt('api_paste_config', default='api-paste.ini',
               help='File name for the paste.deploy config for designate-api'),
    cfg.StrOpt('auth_strategy', default='keystone',
               help='The strategy to use for auth. Supports noauth or '
                    'keystone'),
    cfg.BoolOpt('enable-api-v2', default=True,
                help='enable-api-v2 which enable in a future'),
    cfg.BoolOpt('enable-api-admin', default=False,
                help='enable-api-admin'),
    cfg.IntOpt('max_header_line', default=16384,
               help="Maximum line size of message headers to be accepted. "
                    "max_header_line may need to be increased when using "
                    "large tokens (typically those generated by the "
                    "Keystone v3 API with big service catalogs)."),
]

api_v2_opts = [
    cfg.ListOpt('enabled-extensions-v2', default=[],
                help='Enabled API Extensions for the V2 API'),
    cfg.IntOpt('default-limit-v2', default=20,
               help='Default per-page limit for the V2 API, a value of None '
                    'means show all results by default'),
    cfg.IntOpt('max-limit-v2', default=1000,
               help='Max per-page limit for the V2 API'),
    cfg.BoolOpt('quotas-verify-project-id', default=False,
                help='Verify that the requested Project ID for quota target '
                'is a valid project in Keystone.'),
]

api_admin_opts = [
    cfg.ListOpt('enabled-extensions-admin', default=[],
                help='Enabled Admin API Extensions'),
    cfg.IntOpt('default-limit-admin', default=20,
               help='Default per-page limit for the Admin API, a value of None'
                    ' means show all results by default'),
    cfg.IntOpt('max-limit-admin', default=1000,
               help='Max per-page limit for the Admin API'),
]

api_middleware_opts = [
    cfg.BoolOpt('maintenance-mode', default=False,
                help='Enable API Maintenance Mode'),
    cfg.StrOpt('maintenance-mode-role', default='admin',
               help='Role allowed to bypass maintaince mode'),
    cfg.StrOpt('secure-proxy-ssl-header',
               default='X-Forwarded-Proto',
               help="The HTTP Header that will be used to determine which "
                    "the original request protocol scheme was, even if it was "
                    "removed by an SSL terminating proxy."),
    cfg.StrOpt('override-proto',
               help="A scheme that will be used to override "
                    "the request protocol scheme, even if it was "
                    "set by an SSL terminating proxy.")
]


cfg.CONF.register_group(api_group)
cfg.CONF.register_opts(api_opts, group=api_group)
cfg.CONF.register_opts(api_v2_opts, group=api_group)
cfg.CONF.register_opts(api_admin_opts, group=api_group)
cfg.CONF.register_opts(api_middleware_opts, group=api_group)


def list_opts():
    yield api_group, api_opts
    yield api_group, api_v2_opts
    yield api_group, api_admin_opts
    yield api_group, api_middleware_opts
