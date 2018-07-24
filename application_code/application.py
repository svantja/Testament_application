from application_code.Controller import Controller
from application_code.Tui import Tui
from application_code.connect_main import bigchainDB


class Application:
    def __init__(self):
        self.controller = Controller(bigchainDB())
        self.tui = Tui(self.controller)


class Main:
    app = Application()
    inp = input("input: new User, set up, anmelden, abmelden, "
                "create testament, read testament, file(for test purpose)\n")
    while inp != "q":
        app.tui.process_input(inp)
        inp = input("input: new User, set up, anmelden, abmelden, "
                    "create testament, read testament, file(for test purpose)\n")
        if inp == "q":
            break
