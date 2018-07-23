from application_code.Controller import Controller
from bigchaindb_driver.crypto import generate_keypair

class Tui(Controller):
    def __init__(self, controller):
        self.test = "bb"
        self.b = "gg"
        controller.test = "dfdfdfd"
        self.controller = controller

    def process_input(self, test):
        if test.startswith("new User"):
            role = input("enter user role: (notar, nachlassgericht)")

            while True:
                if role == "notar" or role == "nachlassgericht":
                    print("jaaay")
                    print(role)
                    break
                else:
                    role = input("retry entering, only notar + nachlassgericht are allowed")
            name = input("enter user name")
            keys = generate_keypair()
            self.controller.add_user(name, role, keys.public_key)
            print("new user")
        print("hhh", test)
