from application_code.Controller import Controller
from application_code.Tui import Tui
from application_code.connect_main import bigchainDB


class Application:
    def __init__(self):
        self.controller = Controller()
        self.controller.tui = Tui(self.controller)
        self.controller.bigchaindb= bigchainDB(self.controller)


class Main:
    app = Application()
    inp = ""
    while inp != "q":
        inp = input("input: new User, add to Group, create new Group")
        app.controller.tui.process_input(inp)
        if inp == "q":
            break
