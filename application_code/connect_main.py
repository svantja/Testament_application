import json

from bigchaindb_driver import BigchainDB
import datetime, time


class bigchainDB:
    def __init__(self):
        self.admin = None
        print(self.admin)
        # port to which connect to
        self.db = BigchainDB('192.168.99.100:9984')
        #self.db = None
        self.nameSpace = 'testament'
        # dictionary of user types
        self.user_types = {}
        self.users = {}
        # id of the application
        self.app_id = None
        self.admin_grp_id = None

    # TODO: amtssitzvom notar, standort des nachlassgerichts
    def create_user(self, name, role, user_pub, ort):
        # date == Datum GMT ex.: Mon Jul 23 2018 17:15:24 GMT+0200
        # timestamp == miliseconds ex.:
        d = datetime.datetime.now()
        user_metadata = {
            'event': 'User Assigned',
            'name': name,
            'ort': ort,
            'date': d.strftime('%a %b %d %Y %H:%M:%S %Z'),
            'timestamp': time.mktime(d.timetuple())*1000,
            'publicKey': self.admin['public'],
            'eventData': {
                'userType': role
            }
        }
        user_id = self.create_user_asset(role, user_pub, user_metadata)
        self.users.update({name: user_id})
        return user_id

    def create_new_testament(self, metadata, user_key):
        d = datetime.datetime.now()
        testament_metadata = metadata
        with open('group_types.json') as data_file:
            data_loaded = json.load(data_file)
            testament_grp_id = data_loaded['groups']['testament']
        testament_id = self.create_type_asset('testament', testament_grp_id, testament_metadata, user_key)

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
        # check if types already exist
        check = self.db.assets.get(search='testament.notar')
        check_2 = self.db.assets.get(search='testament.nachlassgericht')

        if len(check) != 0 and len(check_2) != 0:
            print("user types already created")

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
        # TODO: save group_id in .txt File
        return notar_group_id, nachlassgericht_group_id

    # method shall only be called once -> only for initialzation of the database
    # only the admin is later allowed to create new users
    # TODO: login mechanism to verify admin role
    def set_up_admin_role(self):
        #check if already exist
        check = self.db.assets.get(search='testament.admin')
        check_2 = self.db.assets.get(search='testament')

        if len(check) != 0 and len(check_2) != 0:
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
             'can_link': [self.admin['public']]
        }

        admin_group_id = (self.create_new_asset(self.admin, admin_group_asset, admin_group_metadata))['id']
        self.user_types.update({'admin': admin_group_id})
        d = datetime.datetime.now()
        user_metadata = {
            'event': 'User Assigned',
            'name': 'administrator',
            'date': d.strftime('%a %b %d %Y %H:%M:%S %Z'),
            'timestamp': time.mktime(d.timetuple())*1000,
            'publicKey': self.admin['public'],
            'eventData': {
                'userType': 'admin'
            }
        }
        user_id = self.create_user_asset('admin', self.admin['public'], user_metadata)
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

        return app_id, admin_group_id

# method shall only be called once -> only for initialzation of the database
    def create_new_asset(self, keypair, asset, metadata):
        tx = self.db.transactions.prepare(
            operation='CREATE',
            signers=keypair['public'],
            asset=asset,
            metadata=metadata,
        )
        print(tx)
        condition = self.db.transactions.fulfill(tx, private_keys=keypair['private'])
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
        trials += 1

        if condition == sent:
            #creating assets...
            print("failure while creating new asset")
            return sent

        return condition

    def create_type_asset(self, typename, typeid, metadata, user_key):
        asset = {
            'data': {
                'ns': self.nameSpace + '.' + typename,
                'link': typeid,
            }
        }
        self.create_new_asset(user_key, asset, metadata)

    def create_user_asset(self, user_type_name, user_public, user_metadata):
        with open('group_types.json') as data_file:
            data_loaded = json.load(data_file)
            if user_type_name not in data_loaded['groups']:
                print("cannot create user, user group doesn't exists yet")
                return
        link = data_loaded['groups'][user_type_name]
        asset = {
            'data': {
                'ns': self.nameSpace + '.' + user_type_name,
                'link': link,
                'createdBy': self.admin['public'],
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
            'publicKey': self.admin['public'],
            'eventData': {
                'userType': user_type_name
            }
        }

        instance = self.create_new_asset(self.admin, asset, metadata)
        transfer = self.transfer_asset(instance, self.admin, user_public, user_metadata)
        return instance

    def transfer_asset(self, transaction, fromkey, tokey, metadata):
        asset_id = transaction['id']
        transfer_asset = {
            'id': asset_id,
        }
        output_index = 0
        creation_tx = transaction
        output = creation_tx['outputs'][output_index]
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
            private_keys=self.admin['private'],
        )

        sent_transfer = self.db.transactions.send(fulfilled_transfer)
        if sent_transfer == fulfilled_transfer:
            return sent_transfer
        return sent_transfer
