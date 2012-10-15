from _Action import Action

class IgnoreAction(Action):
    def run_on(self, line):
        return None