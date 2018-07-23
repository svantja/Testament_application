from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
import datetime, time


class bigchainDB:
    def __init__(self):
        self.admin = generate_keypair()
        print(self.admin)
        # port to which connect to
        self.db = BigchainDB('192.168.99.100:9984')
        self.nameSpace = 'testament'
        # dictionary of user types
        self.user_types = {}
        self.users = {}
        # id of the application
        self.app_id = self.set_up_admin_role()
        print("app set up")
        # set up the other user-types: notar, nachlassgericht
        self.set_up_types()
        print("types set up")
        # set up the testament type
        self.testament_type_id = self.set_up_testament_type()
        # create admin user
        #self.admin_user = self.create_user('administrator', 'admin', self.admin.public_key)


    def create_user(self, name, role, user_pub):
        # date == Datum GMT ex.: Mon Jul 23 2018 17:15:24 GMT+0200
        # timestamp == miliseconds ex.:
        # Mon Jul 23 2018 17:15:24 GMT+0200
        d = datetime.datetime.now()
        user_metadata = {
            'event': 'User Assigned',
            'name': name,
            'date': d.strftime('%a %b %d %Y %H:%M:%S %Z'),
            'timestamp': time.mktime(d.timetuple())*1000,
            'publicKey': self.admin.public_key,
            'eventData': {
                'userType': role
            }
        }
        user_id = self.create_user_asset(role, user_pub, user_metadata)
        self.users.update({name: user_id})
        return user_id

    def set_up_testament_type(self):
        if 'notar' not in self.user_types:
            print("set up notar type first")
            return
        print("......testament")
        testament_type_asset = {
            'data': {
                'ns': self.nameSpace + '.testament',
                'name': 'testament',
                'link': self.app_id,
            }
        }
        print("notar_grp_id:" + self.user_types['notar'])
        testament_type_metadata = {
            'can_link': self.user_types['notar']
        }

        testament_type_id = (self.create_new_asset(self.admin, testament_type_asset, testament_type_metadata))['id']
        return testament_type_id

    def set_up_types(self):
        print(self.user_types)
        if 'admin' not in self.user_types:
            print("set up admin and app first!")
            return

        notar_group_asset = {
            'data': {
                'ns': self.nameSpace + '.notar',
                'name': 'notar',
                'link': self.app_id,
            }
        }

        notar_group_metadata = {
            'can_link': self.user_types['admin']
        }

        notar_group_id = (self.create_new_asset(self.admin, notar_group_asset, notar_group_metadata))['id']
        print("notar_grp_id:"+ notar_group_id)
        self.user_types.update({'notar': notar_group_id})

        for i in self.user_types.values():
            print(i)

        nachlassgericht_group_asset = {
            'data':{
                'ns': self.nameSpace + 'nachlassgericht',
                'name': 'nachlassgericht',
                'link': self.app_id,
            }
        }

        nachlassgericht_group_metadata = {
            'can_link': self.user_types['admin']
        }

        nachlassgericht_group_id = (self.create_new_asset(self.admin, nachlassgericht_group_asset, nachlassgericht_group_metadata))['id']

        self.user_types.update({'nachlassgericht': nachlassgericht_group_id})

    # method shall only be called once -> only for initialzation of the database
    # only the admin is later allowed to create new users
    # TODO: login mechanism to verify admin role
    def set_up_admin_role(self):
        #check if already exist
        check = self.db.assets.get(search='testament.admin')
        check_2 = self.db.assets.get(search='testament')

        #if len(check) != 0 and len(check_2) != 0:
        #    print("already created")
        #    return

        print("create group asset for admin")

        admin_group_asset = {
            'data': {
                'ns': self.nameSpace + '.admin',
                'name': 'admin',
            },
        }
        admin_group_metadata = {
             'can_link': [self.admin.public_key]
        }

        admin_group_id = (self.create_new_asset(self.admin, admin_group_asset, admin_group_metadata))['id']

        self.user_types.update({'admin': admin_group_id})
        d = datetime.datetime.now()
        user_metadata = {
            'event': 'User Assigned',
            'name': 'administrator',
            'date': d.strftime('%a %b %d %Y %H:%M:%S %Z'),
            'timestamp': time.mktime(d.timetuple())*1000,
            'publicKey': self.admin.public_key,
            'eventData': {
                'userType': 'admin'
            }
        }
        user_id = self.create_user_asset('admin', self.admin.public_key, user_metadata)
        self.users.update({'administrator': user_id})


        app_asset = {
            'data': {
                'ns': self.nameSpace,
                'name': self.nameSpace,
            },
        }

        app_metadata = {
            'can_link': admin_group_id
        }
        print("admin created, fehlt noch app")
        app_id = (self.create_new_asset(self.admin, app_asset, app_metadata))['id']

        return app_id

# method shall only be called once -> only for initialzation of the database
    def create_new_asset(self, keypair, asset, metadata):
        tx = self.db.transactions.prepare(
            operation='CREATE',
            signers=keypair.public_key,
            asset=asset,
            metadata=metadata,
        )
        print(tx)
        condition = self.db.transactions.fulfill(tx, private_keys=keypair.private_key)
        print(condition)
        sent = self.db.transactions.send(condition)
        trials = 0

        while trials < 100:
            try:
                if self.db.transactions.status(condition['id']).get('status') == 'valid':
                    print("valid")
                    break
            except:
                print("exception...")
                trials += 1
        print(trials)
        trials += 1

        print(self.db.transactions.status(condition['id'])['status'])

        print("hhhhh")
        if condition == sent:
            #creating assets...
            print("failure while creating new asset")
            return sent

        return condition

    def create_user_asset(self, user_type_name, user_public, user_metadata):
        if user_type_name not in self.user_types:
            print("cannot create user, user group doesn't exists yet")
            return

        asset = {
            'data': {
                'ns': self.nameSpace + '.' + user_type_name,
                'link': self.user_types[user_type_name],
                'createdBy': self.admin.public_key,
                'type': user_type_name,
                'policy': [
                    {
                        'condition': 'transaction.operation == \'TRANSFER\'',
                        'rule': 'LEN(transaction.outputs[0].public_keys) == 1'
                    },
                    {
                        'condition': 'transaction.operation == \'TRANSFER\'',
                        'rule': 'transaction.outputs[0].public_keys[0] ==\'' + user_public + '\''
                    }
                ],
                'keyword': 'UserAsset'
            },
        }
        d = datetime.datetime.now()
        metadata = {
            'event': 'User Added',
            'date': d.strftime('%a %b %d %Y %H:%M:%S %Z'),
            'timestamp': time.mktime(d.timetuple())*1000,
            'publicKey': self.admin.public_key,
            'eventData': {
                'userType': user_type_name
            }
        }

        instance = self.create_new_asset(self.admin, asset, metadata)
        print("fehlerhier")
        print(instance['id'])
        transfer = self.transfer_asset(instance, self.admin, user_public, user_metadata)
        print(transfer)
        return instance

    def transfer_asset(self, transaction, fromkey, tokey, metadata):
        print(transaction['id'])
        asset_id = transaction['id']
        transfer_asset = {
            'id': asset_id,
        }
        output_index = 0
        creation_tx = transaction
        output = creation_tx['outputs'][output_index]
        #output = transaction['outputs'][output_index]
        transfer_input = {
            'fulfillment': output['condition']['details'],
            'fulfills': {
                'output_index': output_index,
                'transaction_id': asset_id,
            },
            'owners_before': output['public_keys'],
        }
        prepared_transfer = self.db.transactions.prepare(
            operation='TRANSFER',
            asset=transfer_asset,
            inputs=transfer_input,
            recipients=tokey,
            metadata=metadata,
        )

        fulfilled_transfer = self.db.transactions.fulfill(
            prepared_transfer,
            private_keys=self.admin.private_key,
        )

        print("error?")
        print(fulfilled_transfer)
        print(prepared_transfer)
        sent_transfer = self.db.transactions.send(fulfilled_transfer)
        print("error...")
        if sent_transfer == fulfilled_transfer:
            return sent_transfer
        return sent_transfer
