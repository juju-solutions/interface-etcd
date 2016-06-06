from charms.reactive import RelationBase
from charms.reactive import hook
from charms.reactive import scopes


class EtcdPeer(RelationBase):

    scope = scopes.UNIT

    @hook('{peers:etcd}-relation-joined')
    def peer_joined(self):
        conv = self.conversation()
        conv.set_state('{relation_name}.joined')

    @hook('{peers:etcd}-relation-departed')
    def peers_going_away(self):
        '''
            Trigger a state on the unit that will be destroyed.

            The followers are communicating using the leader-data.
        '''
        conv = self.conversation()
        conv.remove_state('{relation_name}.joined')
        conv.set_state('{relation_name}.departing')

    def dismiss(self):
        ''' Mark each conversation that the context is now done, and we can
        resume normal operation.
        '''
        for conv in self.conversations():
            conv.remove_state('{relation_name}.departing')
