
from charms.reactive import RelationBase
from charms.reactive import hook
from charms.reactive import scopes
from os import getenv
from charmhelpers.core.hookenv import unit_get
from charmhelpers.core.hookenv import is_leader

from etcd import databag_to_dict


class EtcdClient(RelationBase):
    ''' ETCD Peering works in tandem with the leader node to establish a cluster
        as sanely as possible. This works statically behind a firewall without
        any need for an external service to function as the discovery mechanism

        Every peer participating in the cluster declares themselves to the
        cluster. The leader then ingests the data and leader-set's the cluster
        state (string, status, token) for the peers to ingest and participate.
    '''
    scope = scopes.UNIT

    auto_accessors = ['private_address', 'public_address', 'port', 'unit_name',
                      'management_port', 'state']

    @hook('{peers:etcd}-relation-joined')
    def peers_joined(self, management_port=7001, port=4001):
        self.set_state('{relation_name}.connected')
        conv = self.conversation()
        unit_name = getenv('JUJU_UNIT_NAME').replace('/', '')
        conv.set_remote(data={'unit_name': unit_name,
                              'management_port': management_port,
                              'port': port,
                              'private_address': unit_get('private-address'),  # noqa
                              'public_address': unit_get('public-address'),
                              'state': 'new'})

    @hook('{peers:etcd}-relation-changed')
    def peers_changed(self):
        conv = self.conversation()
        if is_leader():
            if conv.get_remote('management_port'):
                conv.set_state('{relation_name}.available')

    def peer_map(self):
        etcd_peer_map = {}
        for participant in self.conversations():
            name = participant.scope
            unit = databag_to_dict(participant)
            etcd_peer_map[name] = unit
        import pdb; pdb.set_trace()
        return etcd_peer_map

    @hook('{peers:etcd}-relation{broken,departed}')
    def removal(self, management_port=7001, port=4001):
        self.remove_state('{relation_name}.connected')
        conv = self.conversation()
        unit_name = getenv('JUJU_UNIT_NAME').replace('/', '')
        conv.set_remote(data={'unit_name': unit_name,
                              'management_port': management_port,
                              'port': port,
                              'private_address': unit_get('private-address'),
                              'public_address': unit_get('public-address'),
                              'state': 'dead'})
