from application_code.connect_main import bigchainDB


class Controller(bigchainDB):
    def __init__(self, bigchaindb):
        self.test = "bbbb"
        print(self.test)
        self.bigchaindb = bigchaindb



    def add_user(self, name, role, pub_key):
        user = self.bigchaindb.create_user(name, role, pub_key)
        print(name, role)


