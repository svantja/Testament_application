import io
import json

from werkzeug._compat import to_unicode

from application_code.connect_main import bigchainDB
from bigchaindb_driver.crypto import generate_keypair


class Controller(bigchainDB):
    def __init__(self, bigchaindb):
        self.bigchaindb = bigchaindb

    # add a new user with a specific role (notar, nachlassgericht)
    def add_user(self, name, role, user_keys, ort):
        user_id = self.bigchaindb.create_user(name, role, user_keys['public'], ort)
        # save the users keys, name and role in user_keys.json
        self.save_keys(user_keys, name, role)
        return user_id

    # check if the user exists. if yes, return role, keys and name, else return none
    def check_user(self, name):
        # existing users are stored in user_keys.json. if name is not inside it's not an user
        with open('user_keys.json') as data_file:
            data_loaded = json.load(data_file)
            if name in data_loaded['users']:
                role = data_loaded['users'][name]['role']
                keys = {'public': data_loaded['users'][name]['public'],
                        'private': data_loaded['users'][name]['private']}
                return role, keys, name
            return None, None, None

    # only call once for setup at start
    def set_up(self):
        keys = generate_keypair()
        self.bigchaindb.admin = {'public': keys.public_key, 'private': keys.private_key}
        self.save_keys(self.bigchaindb.admin, 'administrator', 'admin')
        # setup app-asset, admin-asset and admin-instance
        self.bigchaindb.app_id, self.bigchaindb.admin_grp_id = self.bigchaindb.set_up_admin_role()
        # if setup was successful, save id
        if self.bigchaindb.app_id is not None:
            self.save_types(self.bigchaindb.app_id, 'app')
        # if setup was successful, save id
        if self.bigchaindb.admin_grp_id is not None:
            self.save_types(self.bigchaindb.admin_grp_id, 'admin')
        # create admin user
        self.bigchaindb.create_user('administrator', 'admin', self.bigchaindb.admin['public'], None)
        # setup user-group-assets
        notar_type, nachlass_type = self.bigchaindb.set_up_types()
        # if setup was successful, save id
        if notar_type is not None:
            self.save_types(notar_type, 'notar')
        # if setup was successful, save id
        if nachlass_type is not None:
            self.save_types(nachlass_type, 'nachlassgericht')
        # set up testament type-asset
        testament_type = self.bigchaindb.set_up_testament_type()
        if testament_type is not None:
            self.save_types(testament_type, 'testament')

    # for test purpose. no restart of bigchaindb necessary
    def load_old(self):
        with open('user_keys.json') as data_file:
            data_loaded = json.load(data_file)
            if 'administrator' in data_loaded['users']:
                admin = data_loaded['users']['administrator']
                self.bigchaindb.admin = {'public': admin['public'], 'private': admin['private']}
        with open('group_types.json') as data_file:
            data_loaded = json.load(data_file)
            if 'app' in data_loaded['groups']:
                self.bigchaindb.app_id = data_loaded['groups']['app']
            if 'admin' in data_loaded['groups']:
                self.bigchaindb.admin_grp_id = data_loaded['groups']['app']

    # save user keypair, name and role in a .json file
    # not for productive usage: TODO: save user information securely
    def save_keys(self, keypair, name, role):
        # open file and modify content
        with open('user_keys.json') as data_file:
            data_loaded = json.load(data_file)
            data_loaded['users'][name] = {'role': role, 'public': keypair['public'], 'private': keypair['private']}

        # write modified content to file
        with io.open('user_keys.json', 'w', encoding='utf8') as outfile:
            str_ = json.dumps(data_loaded,
                              indent=4, sort_keys=True,
                              separators=(',', ': '), ensure_ascii=False)
            outfile.write(to_unicode(str_))

    # save the names of the type-assets and their ids: for easier usage
    def save_types(self, type_id, name):
        # open file andmodify content
        with open('group_types.json') as data_file:
            data_loaded = json.load(data_file)
            data_loaded['groups'][name] = type_id

        # write modified content to file
        with io.open('group_types.json', 'w', encoding='utf8') as outfile:
            str_ = json.dumps(data_loaded,
                              indent=4, sort_keys=True,
                              separators=(',', ': '), ensure_ascii=False)
            outfile.write(to_unicode(str_))

    # create key_file.json
    def set_up_key_file(self):
        # 'empty' json
        data = {
            'users': {},
        }
        with io.open('user_keys.json', 'w', encoding='utf8') as outfile:
            str_ = json.dumps(data,
                              indent=4, sort_keys=True,
                              separators=(',', ': '), ensure_ascii=False)
            outfile.write(to_unicode(str_))

    # create group_types.json file
    def set_up_types_file(self):
        data = {
            'groups': {},
        }
        with io.open('group_types.json', 'w', encoding='utf8') as outfile:
            str_ = json.dumps(data,
                              indent=4, sort_keys=True,
                              separators=(',', ': '), ensure_ascii=False)
            outfile.write(to_unicode(str_))

    # create new instance of asset-type testament: save custody information
    def create_new_testament(self, data, keys):
        testament = self.bigchaindb.create_new_testament(data, keys)
        print("create new testament. id: " + testament)
        return testament

    def search_testament(self, input):
        self.bigchaindb.search_testament(input)
