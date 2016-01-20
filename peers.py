
from charms.reactive import RelationBase
from charms.reactive import hook
from charms.reactive import scopes
from os import getenv


class EtcdClient(RelationBase):
    scope = scopes.UNIT

    @hook('{peers:etcd}-relation-{joined,changed}')
    def changed(self, management_port=7001):
        conv = self.conversation()
        unit_name = getenv('JUJU_UNIT_NAME').replace('/', '')
        conv.set_remote(data={'unit_name': unit_name,
                              'port': management_port})
