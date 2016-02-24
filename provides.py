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


class EtcdProvider(RelationBase):
    scope = scopes.GLOBAL

    @hook('{provides:etcd}-relation-{joined,changed}')
    def joined_or_changed(self):
        self.set_state('{relation_name}.joined')

    @hook('{provides:etcd}-relation-{broken,departed}')
    def broken_or_departed(self):
        self.remove_state('{relation_name}.joined')

    def provide_connection_string(self, hosts, port):
            connection_string = ""
            for host in hosts:
                connection_string += ",http://{}:{}".format(host, port)
            self.set_remote('connection_string', connection_string.lstrip(','))
            return connection_string.lstrip(',')
