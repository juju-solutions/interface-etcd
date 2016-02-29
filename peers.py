from charms.reactive import RelationBase
from charms.reactive import hook
from charms.reactive import scopes
from charms.reactive import not_unless


class EtcdPeer(RelationBase):
    ''' ETCD Peering works in tandem with the leader node to establish a cluster
        as sanely as possible. This works statically behind a firewall without
        any need for an external service to function as the discovery mechanism

        Every peer participating in the cluster declares themselves to the
        cluster. The leader then ingests the data and leader-set's the cluster
        state (string, status, token) for the peers to ingest and participate.
    '''
    scope = scopes.UNIT

    # kevin - auto_accessors are cool.
    auto_accessors = ['public_address', 'unit_name', 'port']

    @hook('{peers:etcd}-relation-joined')
    def peers_joined(self):
        # As i understand this, this only operates on the conversation in
        # current scope.
        conv = self.conversation()
        conv.set_state('{relation_name}.declare_self')

    @hook('{peers:etcd}-relation-changed')
    def peers_changed(self):
        # As i understand this, this only operates on the conversation in
        # current scope.
        conv = self.conversation()
        # if we get a unit_name, we'll assume we have all the data....
        if conv.get_remote('unit_name'):
            conv.set_state('{relation_name}.joining')

    def private_address(self):
        return self.get_remote('private-address')

    def list_peers(self):
        """
        Return a list of units requesting peering.
        Example usage::
            for unit in etcd.list_peers():
                public_address = unit_get('public-address')
                etcd.provide_cluster_details(**create_peerstring(etcd))
        """
        for conversation in self.conversations():
            unit = conversation.scope
            # yield the current conversation object for the connecting peer
            yield unit

    @not_unless('{relation_name}.joining')
    def provide_cluster_details(self, scope, public_address, port, unit_name):
        '''
        Declare yourself to the cluster as a participating member.
        of etcd. This is used on the leader to calculate the cluster string and
        state of the cluster.

        @param: scope - conversation scope yielded from list_peers
        @param: public_address - units public-address
        @param: port - public port in connection string
        @param: unit_name - charm name/unit# with the / stripped. eg: etcd1
        '''
        conversation = self.conversation(scope=scope)
        conversation.set_remote(port=port, unit_name=unit_name,
                                public_address=public_address)
        conversation.remove_state('{relation_name}.joining')
        conversation.remove_state('{relation_name}.declare_self')
