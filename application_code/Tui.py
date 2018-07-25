import json

from application_code.Controller import Controller
from bigchaindb_driver.crypto import generate_keypair

class Tui(Controller):
    def __init__(self, controller):
        self.controller = controller
        self.role = None
        self.keys = None

    def process_input(self, test):
        if self.role is not None and self.keys is not None:
            if test.startswith("abmelden"):
                self.keys = None
                self.role = None
                print("erfolgreich abgemeldet.\n mit anderem Nutzer anmedel: \n")
                return
            elif test.startswith("create testament"):
                print("create new testament")
                if self.role != "notar":
                    print("must be notar to create new testament")
                    return
                with open('testament_template.json') as data_file:
                    data_loaded = json.load(data_file)
                    data_loaded['erblasser']['vorname'] = input("enter personal data: vorname\n")
                    data_loaded['erblasser']['familienname'] = input("enter personal data: familienname\n")
                    data_loaded['erblasser']['geburtsname'] = input("enter personal data: geburtsname\n")
                    data_loaded['erblasser']['geschlecht'] = input("enter personal data: geschlecht \n")
                    data_loaded['erblasser']['geburtstag'] = input("enter personal data: geburtstag dd.mm.yy\n")
                    data_loaded['erblasser']['geburtsort'] = input("enter personal data: geburtsort\n")
                    data_loaded['erblasser']['geburtsstaat'] = input("enter personal data: geburtsort\n")
                    data_loaded['erblasser']['geburtsstandesamt'] = input("enter personal data: geburtsstandesamt\n")
                    data_loaded['erblasser']['geburtenbuchnummer'] = input("enter personal data: geburtenbuchnummer\n")
                self.controller.create_new_testament(data_loaded, self.keys)

            elif test.startswith("read testament"):
                print("read testament: admin, nachlass, notar")
            elif test.startswith("new User"):
                if self.role != "admin":
                    print("must be admin to add new user")
                    return
                role = input("enter user role: (notar, nachlassgericht"
                             ")\n")
                while True:
                    if role == "notar" or role == "nachlassgericht":
                        print("jaaay")
                        print(role)
                        break
                    else:
                        role = input("retry entering, only notar + nachlassgericht are allowed")
                name = input("enter user name\n")
                keys = generate_keypair()
                self.controller.add_user(name, role, keys)
                print("new user")
        else:
            if test.startswith("anmelden"):
                user = input("enter user name:\n")
                self.role, self.keys = self.controller.check_user(user)
                if self.role is not None and self.keys is not None:
                    print("success")
                    print(generate_keypair())
                    print(self.keys)
                else:
                    print("user doesnt exist")
            # nur einmalig aufrugen
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
                    data = data_loaded['users']['ana']
                    print(data)
                    print(data_loaded)


