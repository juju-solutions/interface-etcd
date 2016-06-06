from charms.reactive import RelationBase
from charms.reactive import hook
from charms.reactive import scopes


class EtcdPeer(RelationBase):

    scope = scopes.UNIT

    # kevin - auto_accessors are cool.

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

    def dismiss(self, unit_id):
        # I dislike the kittens i have to murder to do this
        conv = self.conversation(unit_id)
        self.remove_state('{relation_name}.departing')
