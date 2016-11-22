# Copyright 2012 OpenStack Foundation
# Copyright 2013 IBM Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from keystoneauth1.exceptions import catalog as key_ex

from novaclient import client
from novaclient import exceptions
from novaclient.i18n import _LE
from novaclient.v2 import agents
from novaclient.v2 import aggregates
from novaclient.v2 import availability_zones
from novaclient.v2 import certs
from novaclient.v2 import cloudpipe
from novaclient.v2 import fixed_ips
from novaclient.v2 import flavor_access
from novaclient.v2 import flavors
from novaclient.v2 import floating_ip_dns
from novaclient.v2 import floating_ip_pools
from novaclient.v2 import floating_ips
from novaclient.v2 import floating_ips_bulk
from novaclient.v2 import fping
from novaclient.v2 import hosts
from novaclient.v2 import hypervisors
from novaclient.v2 import images
from novaclient.v2 import keypairs
from novaclient.v2 import limits
from novaclient.v2 import networks
from novaclient.v2 import quota_classes
from novaclient.v2 import quotas
from novaclient.v2 import security_group_default_rules
from novaclient.v2 import security_group_rules
from novaclient.v2 import security_groups
from novaclient.v2 import server_groups
from novaclient.v2 import server_migrations
from novaclient.v2 import servers
from novaclient.v2 import services
from novaclient.v2 import usage
from novaclient.v2 import versions
from novaclient.v2 import virtual_interfaces
from novaclient.v2 import volumes


class Client(object):
    """Top-level object to access the OpenStack Compute API.

    .. warning:: All scripts and projects should not initialize this class
      directly. It should be done via `novaclient.client.Client` interface.
    """

    def __init__(self,
                 api_key=None,
                 api_version=None,
                 auth=None,
                 auth_token=None,
                 auth_url=None,
                 bypass_url=None,
                 cacert=None,
                 connection_pool=False,
                 direct_use=True,
                 endpoint_type='publicURL',
                 extensions=None,
                 http_log_debug=False,
                 insecure=False,
                 logger=None,
                 no_cache=True,
                 os_cache=False,
                 project_id=None,
                 proxy_tenant_id=None,
                 proxy_token=None,
                 username=None,
                 region_name=None,
                 service_name=None,
                 service_type='compute',
                 session=None,
                 tenant_id=None,
                 timeout=None,
                 timings=False,
                 user_id=None,
                 volume_service_name=None,
                 **kwargs):
        """Initialization of Client object.

        :param str api_key: API Key
        :param api_version: Compute API version
        :type api_version: novaclient.api_versions.APIVersion
        :param str auth: Auth
        :param str auth_token: Auth token
        :param str auth_url: Auth URL
        :param str bypass_url: Bypass URL
        :param str cacert: cacert
        :param bool connection_pool: Use a connection pool
        :param direct_use: Inner variable of novaclient. Do not use it outside
            novaclient. It's restricted.
        :param str endpoint_type: Endpoint Type
        :param str extensions: Extensions
        :param bool http_log_debug: Enable debugging for HTTP connections
        :param bool insecure: Allow insecure
        :param logger: Logger
        :param bool no_cache: No cache
        :param bool os_cache: OS cache
        :param str project_id: Project ID
        :param str proxy_tenant_id: Tenant ID
        :param str proxy_token: Proxy Token
        :param str region_name: Region Name
        :param str service_name: Service Name
        :param str service_type: Service Type
        :param str session: Session
        :param str tenant_id: Tenant ID
        :param float timeout: API timeout, None or 0 disables
        :param bool timings: Timings
        :param str user_id: User ID
        :param str username: Username
        :param str volume_service_name: Volume Service Name
        """
        if direct_use:
            raise exceptions.Forbidden(
                403, _LE("'novaclient.v2.client.Client' is not designed to be "
                         "initialized directly. It is inner class of "
                         "novaclient. You should use "
                         "'novaclient.client.Client' instead. Related lp "
                         "bug-report: 1493576"))

        # FIXME(comstud): Rename the api_key argument above when we
        # know it's not being used as keyword argument

        # NOTE(cyeoh): In the novaclient context (unlike Nova) the
        # project_id is not the same as the tenant_id. Here project_id
        # is a name (what the Nova API often refers to as a project or
        # tenant name) and tenant_id is a UUID (what the Nova API
        # often refers to as a project_id or tenant_id).

        password = kwargs.pop('password', api_key)
        self.projectid = project_id
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.flavors = flavors.FlavorManager(self)
        self.flavor_access = flavor_access.FlavorAccessManager(self)
        self.images = images.ImageManager(self)
        self.glance = images.GlanceManager(self)
        self.limits = limits.LimitsManager(self)
        self.servers = servers.ServerManager(self)
        self.versions = versions.VersionManager(self)

        # extensions
        self.agents = agents.AgentsManager(self)
        self.dns_domains = floating_ip_dns.FloatingIPDNSDomainManager(self)
        self.dns_entries = floating_ip_dns.FloatingIPDNSEntryManager(self)
        self.cloudpipe = cloudpipe.CloudpipeManager(self)
        self.certs = certs.CertificateManager(self)
        self.floating_ips = floating_ips.FloatingIPManager(self)
        self.floating_ip_pools = floating_ip_pools.FloatingIPPoolManager(self)
        self.fping = fping.FpingManager(self)
        self.volumes = volumes.VolumeManager(self)
        self.keypairs = keypairs.KeypairManager(self)
        self.networks = networks.NetworkManager(self)
        self.neutron = networks.NeutronManager(self)
        self.quota_classes = quota_classes.QuotaClassSetManager(self)
        self.quotas = quotas.QuotaSetManager(self)
        self.security_groups = security_groups.SecurityGroupManager(self)
        self.security_group_rules = \
            security_group_rules.SecurityGroupRuleManager(self)
        self.security_group_default_rules = \
            security_group_default_rules.SecurityGroupDefaultRuleManager(self)
        self.usage = usage.UsageManager(self)
        self.virtual_interfaces = \
            virtual_interfaces.VirtualInterfaceManager(self)
        self.aggregates = aggregates.AggregateManager(self)
        self.hosts = hosts.HostManager(self)
        self.hypervisors = hypervisors.HypervisorManager(self)
        self.hypervisor_stats = hypervisors.HypervisorStatsManager(self)
        self.services = services.ServiceManager(self)
        self.fixed_ips = fixed_ips.FixedIPsManager(self)
        self.floating_ips_bulk = floating_ips_bulk.FloatingIPBulkManager(self)
        self.os_cache = os_cache or not no_cache
        self.availability_zones = \
            availability_zones.AvailabilityZoneManager(self)
        self.server_groups = server_groups.ServerGroupsManager(self)
        self.server_migrations = \
            server_migrations.ServerMigrationsManager(self)

        # Add in any extensions...
        if extensions:
            for extension in extensions:
                if extension.manager_class:
                    setattr(self, extension.name,
                            extension.manager_class(self))

        if not logger:
            logger = logging.getLogger(__name__)

        self.client = client._construct_http_client(
            username=username,
            password=password,
            api_version=api_version,
            auth=auth,
            auth_token=auth_token,
            auth_url=auth_url,
            bypass_url=bypass_url,
            cacert=cacert,
            connection_pool=connection_pool,
            endpoint_type=endpoint_type,
            http_log_debug=http_log_debug,
            insecure=insecure,
            logger=logger,
            os_cache=self.os_cache,
            project_id=project_id,
            proxy_tenant_id=proxy_tenant_id,
            proxy_token=proxy_token,
            region_name=region_name,
            service_name=service_name,
            service_type=service_type,
            session=session,
            tenant_id=tenant_id,
            timeout=timeout,
            timings=timings,
            user_id=user_id,
            volume_service_name=volume_service_name,
            **kwargs)

    @property
    def api_version(self):
        return self.client.api_version

    @api_version.setter
    def api_version(self, value):
        self.client.api_version = value

    @client._original_only
    def __enter__(self):
        self.client.open_session()
        return self

    @client._original_only
    def __exit__(self, t, v, tb):
        self.client.close_session()

    @client._original_only
    def set_management_url(self, url):
        self.client.set_management_url(url)

    def get_timings(self):
        return self.client.get_timings()

    def reset_timings(self):
        self.client.reset_timings()

    def has_neutron(self):
        """Check the service catalog to figure out if we have neutron.

        This is an intermediary solution for the window of time where
        we still have nova-network support in the client, but we
        expect most people have neutron. This ensures that if they
        have neutron we understand, we talk to it, if they don't, we
        fail back to nova proxies.
        """
        try:
            endpoint = self.client.get_endpoint(service_type='network')
            if endpoint:
                return True
            return False
        except key_ex.EndpointNotFound:
            return False

    @client._original_only
    def authenticate(self):
        """Authenticate against the server.

        Normally this is called automatically when you first access the API,
        but you can call this method to force authentication right now.

        Returns on success; raises :exc:`exceptions.Unauthorized` if the
        credentials are wrong.
        """
        self.client.authenticate()
