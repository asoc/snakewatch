import Action

class IgnoreAction(Action):
    def run_on(self, line):
        return ''