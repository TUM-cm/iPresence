
class Input:
    config = ""
    # Input parameters: config=<filename>
    def __init__(self, args):
        for arg in args[1:]:
            if "config" in arg:
                Input.config = arg.split("=")[1]
