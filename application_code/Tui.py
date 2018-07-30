import json

from application_code.Controller import Controller
from bigchaindb_driver.crypto import generate_keypair

class Tui(Controller):
    def __init__(self, controller):
        self.controller = controller
        self.role = None
        self.keys = None
        self.name = None

    def process_input(self, command):
        if self.role is not None and self.keys is not None:
            # 'Logout' current user
            if command.startswith("Logout"):
                self.keys = None
                self.role = None
                print("erfolgreich abgemeldet.\n mit anderem Nutzer anmedel: \n")
                return
            # create new instance of type-asset testament
            elif command.startswith("create testament"):
                # check if logged in user has the role 'notar'
                if self.role != "notar":
                    print("must be notar to create new testament")
                    return
                # load custody information template and update the values
                with open('testament_template.json') as data_file:
                    data_loaded = json.load(data_file)
                    data_loaded['erblasser']['vorname'] = input("enter personal data: vorname\n")
                    data_loaded['erblasser']['familienname'] = input("enter personal data: familienname\n")
                    data_loaded['erblasser']['geburtsname'] = input("enter personal data: geburtsname\n")
                    data_loaded['erblasser']['geschlecht'] = input("enter personal data: geschlecht \n")
                    data_loaded['erblasser']['geburtstag'] = input("enter personal data: geburtstag dd.mm.yy\n")
                    data_loaded['erblasser']['geburtsort'] = input("enter personal data: geburtsort\n")
                    data_loaded['erblasser']['geburtsstaat'] = input("enter personal data: geburtsstaat\n")
                    data_loaded['erblasser']['geburtsstandesamt'] = input("enter personal data: geburtsstandesamt\n")
                    data_loaded['erblasser']['geburtenbuchnummer'] = input("enter personal data: geburtenbuchnummer\n")
                    data_loaded['urkunde']['art'] = input('enter type of document:\n')
                    data_loaded['urkunde']['datum'] = input('enter the date of document:\n')
                    data_loaded['urkunde']['notar']['name'] = self.name
                    # in Version 2.0 with self.controller.bigchaindb.db.metadata.get(search="\name\\","\notar\")
                    # it would be possible to search for the 'amtssitz'
                    data_loaded['urkunde']['notar']['amtssitz'] = input('enter the notarys\'s office :\n')
                    data_loaded['urkunde']['urkundenrollennummer'] = input('enter the certificate roll number:\n')
                    data_loaded['verwahrung']['analog']['verwahrstelle']['bezeichnung'] = \
                        input("enter the description of the depository institution:\n")
                    data_loaded['verwahrung']['analog']['verwahrstelle']['anschrift'] = \
                        input("enter the address of the depositary:\n")
                    data_loaded['verwahrung']['analog']['verwahrkennzeichen']['verwahrbuchnummer'] = \
                        input("enter ledger number:\n")
                    data_loaded['verwahrung']['analog']['verwahrkennzeichen']['aktenzeichen'] = \
                        input("enter reference numer:\n")
                    data_loaded['verwahrung']['analog']['verwahrkennzeichen']['urkundenrollennummer'] = \
                        data_loaded['urkunde']['urkundenrollennummer']
                    # when IPFS connection is implemented the destination of the file inside there will be stored
                    data_loaded['verwahrung']['digital']['ablageort'] = input("enter destination in IPFS:\n")
                testament = self.controller.create_new_testament(data_loaded, self.keys)
            # search for specific custody information and return location of the actual documents
            elif command.startswith("read testament"):
                inp_erb = {'erblasser': input("enter search parameter.\n erblasser:")}
                self.controller.search_testament(inp_erb)
                print("read testament: admin, nachlass, notar")
            # create new User
            elif command.startswith("new User"):
                # check if the logged in user has the role 'admin'
                if self.role != "admin":
                    print("must be admin to add new user")
                    return
                # select the desired role
                role = input("enter user role: (notar, nachlassgericht"
                             ")\n")
                # check the user input: user can only be created if role exists. here: notar and nachlassgericht
                while True:
                    if role == "notar" or role == "nachlassgericht":
                        break
                    else:
                        role = input("retry entering, only notar + nachlassgericht are allowed")
                name = input("enter user name\n")
                # create public and private keypair for the new user
                keys = generate_keypair()
                keys = {'public': keys.public_key, 'private': keys.private_key}
                if role == "notar":
                    ort = input("enter amtssitz:\n")
                else:
                    ort = input("enter standort:\n")
                user_id = self.controller.add_user(name, role, keys, ort)
                print("new user successfully added. User id: " + user_id + "\n")
        else:
            # Login user
            if command.startswith("Login"):
                user = input("enter user name:\n")
                # check if user exists
                self.role, self.keys, self.name = self.controller.check_user(user)
                if self.role is not None and self.keys is not None:
                    print("Login was successful. Now logged in: " + user + "\n")
                else:
                    print("user doesnt exist")
            # only call setup once
            # set up the files where data is saved
            # set up bigchaindb and mongodb
            elif command.startswith("set up"):
                self.controller.set_up_key_file()
                self.controller.set_up_types_file()
                self.controller.set_up()
            elif command.startswith("load old set up"):
                self.controller.load_old()
            # test case, works without bighaindb
            # check if key_file has been created correctly
            elif command.startswith("file"):
                self.controller.set_up_key_file()
                self.controller.save_keys(generate_keypair(), "ana", "admin")
                self.controller.save_keys(generate_keypair(), "blub", "notar")
                with open('user_keys.json') as data_file:
                    data_loaded = json.load(data_file)
                    data = data_loaded['users']['ana']
                    print(data)
                    print(data_loaded)


