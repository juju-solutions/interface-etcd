#!/usr/bin/python
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from charms.reactive import RelationBase
from charms.reactive import hook
from charms.reactive import scopes
from charmhelpers.core.hookenv import is_leader
from charmhelpers.core.hookenv import config
from charmhelpers.core import unitdata


class EtcdProvider(RelationBase):
    scope = scopes.GLOBAL

    @hook('{provides:etcd}-relation-{joined,changed}')
    def joined_or_changed(self):
        if is_leader():
            cstring = self.connection_string()
            self.set_remote(data={'connection_string': cstring})

    def connection_string(self):
        if is_leader():
            db = unitdata.kv()
            cluster_data = db.get('etcd.cluster_data')
            connection_string = ""
            for u in cluster_data:
                connection_string += ",http://{}:{}".format(cluster_data[u]['private_address'], config('port'))  # noqa
            return connection_string.lstrip(',')

    def cluster_data(self, unit=None):
        db = unitdata.kv()
        return db.get('etcd.cluster_data')
