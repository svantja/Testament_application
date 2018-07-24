import json

from application_code.Controller import Controller
from bigchaindb_driver.crypto import generate_keypair

class Tui(Controller):
    def __init__(self, controller):
        self.controller = controller

    def process_input(self, test):
        if test.startswith("new User"):
            role = input("enter user role: (notar, nachlassgericht"
                         ")")

            while True:
                if role == "notar" or role == "nachlassgericht":
                    print("jaaay")
                    print(role)
                    break
                else:
                    role = input("retry entering, only notar + nachlassgericht are allowed")
            name = input("enter user name")
            keys = generate_keypair()
            # TODO: save keypair in .txt File: {role: {name: {public: key, private: key}}}
            self.controller.add_user(name, role, keys.public_key)
            print("new user")
        elif test.startswith("set up"):
            self.controller.set_up_key_file()
            self.controller.set_up_types_file()
            self.controller.set_up()
        elif test.startswith("file"):
            self.controller.set_up_key_file()
            self.controller.save_keys(generate_keypair(), "ana", "admin")
            self.controller.save_keys(generate_keypair(), "blub", "notar")
            with open('user_keys.json') as data_file:
                data_loaded = json.load(data_file)
                print(data_loaded)

        print("hhh", test)
