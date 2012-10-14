from colorama import Fore, Back, Style

from Action import Action

class PrintAction(Action):
    def run_on(self, line):
        style = Style.RESET_ALL
        if 'fore' in self.cfg and hasattr(Fore, self.cfg['fore']):
            style = '%s%s' % (style, getattr(Fore, self.cfg['fore']))
        if 'back' in self.cfg and hasattr(Back, self.cfg['back']):
            style = '%s%s' % (style, getattr(Back, self.cfg['back']))
        if 'style' in self.cfg and hasattr(Style, self.cfg['style']):
            style = '%s%s' % (style, getattr(Style, self.cfg['style']))
        return '%s%s' % (style, line)