from application_code.Controller import Controller


class Tui(Controller):
    def __init__(self, controller):
        self.test = "bb"
        self.b = "gg"
        controller.test = "dfdfdfd"
        self.controller = controller

    def process_input(self, test):
        if test.startswith("new User"):
            self.controller.add_user("hh", "hh")
            print("new user")
        elif test.startswith("add to Group"):
            self.controller.add_to_group("hh", "hh")
            print("add to group")
        elif test.startswith("create new Group"):
            self.controller.add_group("hh", "hh")
            print("new group")
        print("hhh", test)
