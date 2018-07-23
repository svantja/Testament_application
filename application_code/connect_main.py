from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
import json
from application_code.Controller import Controller


class bigchainDB():
    def __init__(self, controller):
        self.admin = generate_keypair()
        print(self.admin)
        self.db = BigchainDB('192.168.99.100:9984')
        self.nameSpace = 'testament'
        self.app_id = None
        self.set_up_admin_role()

    # method shall only be called once -> only for initialzation of the database
    # only the admin is later allowed to create new users
    # TODO: login mechanism to verify admin role
    def set_up_admin_role(self):
        #check if already exist
        check = self.db.assets.get(search='testament.admin')
        check_2 = self.db.assets.get(search='testament')


        if(len(check) != 0 and len(check_2) != 0):
            print("already created")
            return

        print("create group asset for admin")

        admin_group_asset = {
            'data': {
                'ns': self.nameSpace + '.admin',
                'name': 'admin',
            },
        }
        admin_group_metadata = {
             'canLink': [self.admin.public_key]
        }

        admin_group_id = (self.create_new_asset(self.admin, admin_group_asset, admin_group_metadata))['id']

        print("create app asset for application")
        app_asset ={
            'data': {
                'ns': self.nameSpace,
                'name': self.nameSpace,
            },
        }
        app_metadata= {
            'canLink': admin_group_id
        }
        app_id = (self.create_new_asset(self.admin, app_asset, app_metadata))['id']


    def create_user_role(self, admin_keypair, asset, metadata):


    def create_new_asset(self, keypair, asset, metadata):
        tx = self.db.transactions.prepare(
            operation='CREATE',
            signers=keypair.public_key,
            asset=asset,
            metadata=metadata,
        )
        print(tx)
        condition = self.db.transactions.fulfill(tx, private_keys=keypair.private_key)
        sent = self.db.transactions.send(condition)
        return condition



 
