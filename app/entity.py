class BlackInfo(object):
    def __init__(self, id, remark, type, createtime, state, create_person, create_mode):
        self.id = id
        self.remark = remark
        self.type = type
        self.createtime = createtime
        self.state = state
        self.create_person = create_person
        self.create_mode = create_mode

    def __repr__(self):
        return '<BlackInfo %s>' % self.id