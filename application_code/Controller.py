import io
import json

from werkzeug._compat import to_unicode

from application_code.connect_main import bigchainDB
from bigchaindb_driver.crypto import generate_keypair


class Controller(bigchainDB):
    def __init__(self, bigchaindb):
        self.bigchaindb = bigchaindb

    def add_user(self, name, role, user_keys):
        user_id = self.bigchaindb.create_user(name, role, user_keys.public_key)
        self.save_keys(user_keys, name, role)
        print(name, role)

    def check_user(self, name):
        with open('user_keys.json') as data_file:
            data_loaded = json.load(data_file)
            if name in data_loaded['users']:
                role = data_loaded['users'][name]['role']
                keys = {data_loaded['users'][name]['public'], data_loaded['users'][name]['private']}
                return role, keys
            return None, None

    # nur einmalig aufrufen
    def set_up(self):
        keys = generate_keypair()
        self.bigchaindb.admin = {'public': keys.public_key, 'private': keys.private_key}
        self.save_keys(self.bigchaindb.admin, 'svenja', 'admin')
        self.bigchaindb.app_id, self.bigchaindb.admin_grp_id = self.bigchaindb.set_up_admin_role()
        self.save_types(self.bigchaindb.app_id, 'app')
        self.save_types(self.bigchaindb.admin_grp_id, 'admin')
        notar_type, nachlass_type = self.bigchaindb.set_up_types()
        self.save_types(notar_type, 'notar')
        self.save_types(nachlass_type, 'nachlassgericht')
        testament_type = self.bigchaindb.set_up_testament_type()
        self.save_types(testament_type, 'testament')

    def save_keys(self, keypair, name, role):
        # open file and modifie content
        with open('user_keys.json') as data_file:
            data_loaded = json.load(data_file)
            data_loaded['users'][name] = {'role': role, 'public': keypair.public_key, 'private': keypair.private_key}

        # write modified content to file
        with io.open('user_keys.json', 'w', encoding='utf8') as outfile:
            str_ = json.dumps(data_loaded,
                              indent=4, sort_keys=True,
                              separators=(',', ': '), ensure_ascii=False)
            outfile.write(to_unicode(str_))

    def save_types(self, type_id, name):
        # open file andmodify content
        with open('group_types.json') as data_file:
            data_loaded = json.load(data_file)
            data_loaded['groups'][name] = type_id

        # write modified content to file
        with io.open('group_id.json', 'w', encoding='utf8') as outfile:
            str_ = json.dumps(data_loaded,
                              indent=4, sort_keys=True,
                              separators=(',', ': '), ensure_ascii=False)
            outfile.write(to_unicode(str_))

    def set_up_key_file(self):
        data = {
            'users': {},
        }
        with io.open('user_keys.json', 'w', encoding='utf8') as outfile:
            str_ = json.dumps(data,
                              indent=4, sort_keys=True,
                              separators=(',', ': '), ensure_ascii=False)
            outfile.write(to_unicode(str_))

        with open('user_keys.json') as data_file:
            data_loaded = json.load(data_file)
            print(data_loaded)

    def set_up_types_file(self):
        data = {
            'groups': {},
        }
        with io.open('group_types.json', 'w', encoding='utf8') as outfile:
            str_ = json.dumps(data,
                              indent=4, sort_keys=True,
                              separators=(',', ': '), ensure_ascii=False)
            outfile.write(to_unicode(str_))

        with open('group_types.json') as data_file:
            data_loaded = json.load(data_file)
            print(data_loaded)

    def create_new_testament(self, data, keys):
        print("create new testament with " + data + " from " + keys)
