import json

from bigchaindb_driver import BigchainDB
import datetime, time


class bigchainDB:
    def __init__(self):
        self.admin = None
        # port to which connect to
        self.db = BigchainDB('192.168.99.100:9984')
        self.nameSpace = 'testament'
        # id of the application
        self.app_id = None
        self.admin_grp_id = None

    # create new user: add new user to application
    def create_user(self, name, role, user_pub, ort):
        # date == Datum GMT ex.: Mon Jul 23 2018 17:15:24 GMT+0200
        # timestamp == miliseconds ex.:
        d = datetime.datetime.now()
        # metadata for new user
        # if ort is None: admin user
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

        user_id = self.create_user_asset(role, user_pub, user_metadata)['id']
        return user_id

    # create new instance of asset-type testament: save custody information
    def create_new_testament(self, metadata, user_key):
        # set metadata for new instance of type testament to user input (testament_template.json)
        testament_metadata = metadata
        # get testament typ-asset id (group-asset id)
        with open('group_types.json') as data_file:
            data_loaded = json.load(data_file)
            testament_grp_id = data_loaded['groups']['testament']
        # create testament instance
        testament_id = self.create_testament_asset('testament', testament_grp_id, testament_metadata, user_key)
        return testament_id

    def search_testament(self, input):
        # (search="\"testament.testament\"\\\"document\"")
        list_of_testaments = self.db.assets.get(search="\"testament.testament\"")
        for testament in list_of_testaments:
            id = testament['id']
            testament_asset = self.db.transactions.get(asset_id=id, operation='CREATE')[0]
            # erblasser, daten der urkunde, daten der verwahrung
            length = len(input.keys())
            for key in input:
                if key in testament_asset['metadata']:
                    print(key)
                    if input[key] in testament_asset['metadata'][key].values():
                        print("yaaaaay")
                        length = length - 1
            if length == 0:
                print("testament found: " + testament_asset['metadata']['verwahrung']['digital']['ablageort'])




    # set up type-asset testament
    def set_up_testament_type(self):
        # check if asset-type notar was created before. only for secure reasons, shouldn't happen
        with open('group_types.json') as data_file:
            data_loaded = json.load(data_file)
            if 'notar' not in data_loaded['groups']:
                print("set up notar type first")
                return None
            else:
                testament_type_asset = {
                    'data': {
                        'ns': self.nameSpace + '.testament',
                        'name': 'testament',
                        'link': self.app_id,
                    }
                }
                # can_link to notar type-asset (notar-group-id):
                # only notar users can create new instances of type testament
                testament_type_metadata = {
                    'can_link': data_loaded['groups']['notar']
                }

                testament_type_id = (self.create_new_asset(self.admin, testament_type_asset, testament_type_metadata))['id']
        return testament_type_id

    # set up user roles: create type-asset for each role
    def set_up_types(self):
        # check if asset-types admin and app were created before. only for secure reasons, shouldn't happen
        with open('group_types.json') as data_file:
            data_loaded = json.load(data_file)
            if 'admin' not in data_loaded['groups'] or 'app' not in data_loaded['groups']:
                print("set up admin and app first!")
                return None, None
            # check if types notar and nachlassgericht already exist
            if 'notar' in data_loaded['groups'] or 'nachlassgericht' in data_loaded['groups']:
                print("user types already created")
                return None, None

        # create asset for notar type asset
        notar_group_asset = {
            'data': {
                'ns': self.nameSpace + '.notar',
                'name': 'notar',
                'link': self.app_id,
            }
        }
        with open('group_types.json') as data_file:
            data_loaded = json.load(data_file)
            admin_group_id = data_loaded['groups']['admin']
        # can_link to admin: only admin user can create new instances of type notar
        notar_group_metadata = {
            'can_link': admin_group_id
        }
        notar_group_id = (self.create_new_asset(self.admin, notar_group_asset, notar_group_metadata))['id']

        # create asset for nachlass type asset
        nachlassgericht_group_asset = {
            'data':{
                'ns': self.nameSpace + 'nachlassgericht',
                'name': 'nachlassgericht',
                'link': self.app_id,
            }
        }
        # can_link to admin: only admin user can create new instances of type nachlassgericht
        nachlassgericht_group_metadata = {
            'can_link': admin_group_id
        }
        nachlassgericht_group_id = (self.create_new_asset(self.admin, nachlassgericht_group_asset, nachlassgericht_group_metadata))['id']

        return notar_group_id, nachlassgericht_group_id

    # method shall only be called once -> only for initialzation of the database
    # only the admin is later allowed to create new users
    # TODO: login mechanism to verify admin role
    def set_up_admin_role(self):
        #check if already exist
        with open('group_types.json') as data_file:
            data_loaded = json.load(data_file)
            if 'admin' in data_loaded['groups'] or 'app' in data_loaded['groups']:
                print("already created")
                return None, None

        admin_group_asset = {
            'data': {
                'ns': self.nameSpace + '.admin',
                'name': 'admin',
            },
        }
        # can_link to public_key of the new admin: only admin user can create new instances of type admin
        admin_group_metadata = {
             'can_link': [self.admin['public']]
        }
        admin_group_id = (self.create_new_asset(self.admin, admin_group_asset, admin_group_metadata))['id']

        app_asset = {
            'data': {
                'ns': self.nameSpace,
                'name': self.nameSpace,
            },
        }
        # can_link to type-asset admin (admin-group-id): only admin user can create new instances of type app
        app_metadata = {
            'can_link': admin_group_id
        }
        app_id = (self.create_new_asset(self.admin, app_asset, app_metadata))['id']

        return app_id, admin_group_id

    # CREATE Transaction: create assets. keypair represents the signing user
    def create_new_asset(self, keypair, asset, metadata):
        # prepare the transaction: declare which type of transaction (CREATE or TRANSFER)
        # set the authoring user/s (signers): public keys of the user/s
        # define which asset should be created and the metadata of the transaction
        tx = self.db.transactions.prepare(
            operation='CREATE',
            signers=keypair['public'],
            asset=asset,
            metadata=metadata,
        )
        # fullfill the transaction: private key must match the given public key of the signer/s
        condition = self.db.transactions.fulfill(tx, private_keys=keypair['private'])
        # send the fulfilled transaction
        sent = self.db.transactions.send(condition)
        # try up to 100 times to check the status of the issued transaction until it's valid
        trials = 0
        while trials < 100:
            try:
                if self.db.transactions.status(condition['id']).get('status') == 'valid':
                    break
            except:
                trials += 1
        trials += 1

        return condition

    # create new instance of type-asset testament with the given user input of the custody information
    def create_testament_asset(self, typename, typeid, metadata, user_key):
        # set parent to 'link': parent of this asset will be set to the given typeid and it's type-asset
        # her the typeid is the id of the type-asset testament
        asset = {
            'data': {
                'ns': self.nameSpace + '.' + typename,
                'name': 'document',
                'link': typeid,
            }
        }
        asset = self.create_new_asset(user_key, asset, metadata)['id']
        return asset

    # create instance of type-asset of the user role 'user_type_name'
    def create_user_asset(self, user_type_name, user_public, user_metadata):
        # check if the type-asset of the user role exists. otherwise no instance of it can be created
        with open('group_types.json') as data_file:
            data_loaded = json.load(data_file)
            if user_type_name not in data_loaded['groups']:
                print("cannot create user, user group doesn't exists yet")
                return
        # set parent to 'link':
        # parent of this asset will be set to the id of the type-asset of user_type_name and it's type-asset
        link = data_loaded['groups'][user_type_name]
        asset = {
            'data': {
                'ns': self.nameSpace + '.' + user_type_name,
                'link': link,
                'createdBy': self.admin['public'],
                'type': user_type_name,
                'policy': [
                    {
                        # the following transaction containing this asset must be a TRANSFER transaction
                        'condition': 'transaction.operation == \'TRANSFER\'',
                        # the output must be exactly 1: only ONE user is created
                        'rule': 'LEN(transaction.outputs[0].public_keys) == 1'
                    },
                    {
                        # the following transaction containing this asset must be a TRANSFER transaction
                        'condition': 'transaction.operation == \'TRANSFER\'',
                        # the output must be the public key of the new user:
                        # ensures that the correct public key is addresses in the transaction
                        'rule': 'transaction.outputs[0].public_keys[0] ==\'' + user_public + '\''
                    }
                ],
                'keyword': 'UserAsset'
            },
        }
        d = datetime.datetime.now()
        # metadata of the asset which should be created
        metadata = {
            'event': 'User Added',
            'date': d.strftime('%a %b %d %Y %H:%M:%S %Z'),
            'timestamp': time.mktime(d.timetuple())*1000,
            'publicKey': self.admin['public'],
            'eventData': {
                'userType': user_type_name
            }
        }
        # create new asset/instance
        instance = self.create_new_asset(self.admin, asset, metadata)
        # transfer the asset to the new user(public key): user is the new owner of this asset
        # -> new user creation complete
        transfer = self.transfer_asset(instance, self.admin['public'], user_public, user_metadata)
        return instance

    # transfer an asset to someone (tokey == public key)
    def transfer_asset(self, asset, fromkey, tokey, metadata):
        # get the id of the asset which should be transfered
        asset_id = asset['id']
        transfer_asset = {
            'id': asset_id,
        }
        output_index = 0
        creation_tx = asset
        # the output of the asset which should be transfered
        output = creation_tx['outputs'][output_index]
        # the input of the TRANSFER transaction
        transfer_input = {
            'fulfillment': output['condition']['details'],
            'fulfills': {
                'output_index': output_index,
                'transaction_id': asset_id,
            },
            'owners_before': [fromkey],
        }
        # prepare the TRANSFER transaction
        prepared_transfer = self.db.transactions.prepare(
            operation='TRANSFER',
            asset=transfer_asset,
            inputs=transfer_input,
            recipients=tokey,
            metadata=metadata,
        )
        # fulfill the transaction: the private key of the issuer should be the same
        fulfilled_transfer = self.db.transactions.fulfill(
            prepared_transfer,
            private_keys=self.admin['private'],
        )
        # send the transation
        sent_transfer = self.db.transactions.send(fulfilled_transfer)
        return sent_transfer
