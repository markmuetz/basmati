# Thanks: http://stackoverflow.com/a/287944/54557
class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def print(msg, styles=[]):
        colour_style = []
        for style in styles:
            colour_style.append(getattr(Bcolors, style.upper()))
        colour_style = ''.join(colour_style)
        print(colour_style + str(msg) + Bcolors.ENDC)
