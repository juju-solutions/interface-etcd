from charms.reactive import RelationBase
from charms.reactive import hook
from charms.reactive import scopes
from os import getenv
from charmhelpers.core.hookenv import unit_get
from charmhelpers.core.hookenv import is_leader
from etcd import remove_unit_from_cache
from etcd import EtcdHelper

# WARNING! This interface layer assumes that ETCD is present on the
# host that is invoking this relationship handler. As much as I wanted
# to keep concerns separate, the API messaging living here makes sense, but
# negates any concerns of encapsulation.
# TODO: fix and remove the above message


class EtcdClient(RelationBase):
    ''' ETCD Peering works in tandem with the leader node to establish a cluster
        as sanely as possible. This works statically behind a firewall without
        any need for an external service to function as the discovery mechanism

        Every peer participating in the cluster declares themselves to the
        cluster. The leader then ingests the data and leader-set's the cluster
        state (string, status, token) for the peers to ingest and participate.
    '''
    scope = scopes.UNIT

    auto_accessors = ['private_address', 'public_address', 'unit_name']

    @hook('{peers:etcd}-relation-joined')
    def peers_joined(self):
        # As i understand this, this only operates on the conversation in
        # current scope.
        conv = self.conversation()
        conv.set_state('{relation_name}.connected')
        etcd = EtcdHelper()
        conv.set_remote(data={'unit_name': etcd.unit_name,
                              'private-address': etcd.private_address,  # noqa
                              'public-address': etcd.public_address})

    @hook('{peers:etcd}-relation-changed')
    def peers_changed(self):
        ''' This is where we need to raise on the leader node, PER CONVERSATION,
            that the peer has joined, and is self-registering.
        '''
        conv = self.conversation()
        if is_leader():
            if conv.get_remote('public-address'):
                conv.set_state('{relation_name}.joining')

    @hook('{peers:etcd}-relation-{broken,departed}')
    def removal(self):
        ''' Sad days, a unit is being removed. Expire their cache entry and
            begin disturbing the cluster to unregister the member from quorem.
            hopefully before they restart.
        '''
        conv = self.conversation()
        conv.remove_state('{relation_name}.connected')
        # expire cache
        departing_peer = conv.get_remote('unit_name')
        # if we have a unit_name on the wire, assume they are dead to us. RIP
        if departing_peer:
            remove_unit_from_cache(departing_peer)
            conv.set_state('{relation_name}.departed')
        # We always send our data out over the wire... if we are not the leader
        if not is_leader():
            etcd = EtcdHelper()
            conv.set_remote(data={'unit_name': etcd.unit_name,
                                  'private-address': etcd.public_address,
                                  'public-address': etcd.private_address})
