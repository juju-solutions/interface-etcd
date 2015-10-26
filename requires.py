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

from charmhelpers.core import hookenv


class EtcdClient(RelationBase):
    scope = scopes.GLOBAL

    auto_accessors = ['host']

    def port(self):
        """
        Get the port.

        If not available, returns the default port of 4001
        """
        return self.get_remote('port', 4001)

    @hook('{requires:etcd}-relation-{joined,changed}')
    def changed(self):
        self.set_state('{relation_name}.connected')
        hookenv.status_set('maintenance', 'ETCD Node connected...')
        if self.connection_string():
            self.set_state('{relation_name}.available')
            hookenv.status_set('maintenance', 'ETCD data available')

    def connection_string(self):
        """
        Get the connection string, if available, or None.
        """
        data = {'host': self.get_remote('hostname'),
                'port': self.port()
                }

        if all(data.values()):
            return str.format('http://{host}:{port}', **data)
        return None
