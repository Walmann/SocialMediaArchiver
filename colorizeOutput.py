class ColorizeOutput:
    @classmethod
    def colorize(cls, inputC, pcolor):
        return f"{pcolor}{inputC}\033[0m"
    @classmethod
    def HEADER(cls, input):
        print(cls.colorize(inputC=input, pcolor="\033[95m"))
        return
    @classmethod
    def OKBLUE(cls, input):
        print(cls.colorize(inputC=input, pcolor="\033[94m"))
        return
    @classmethod
    def OKCYAN(cls, input):
        print(cls.colorize(inputC=input, pcolor="\033[96m"))
        return
    @classmethod
    def OKGREEN(cls, input):
        print(cls.colorize(inputC=input, pcolor="\033[92m"))
        return
    @classmethod
    def WARNING(cls, input):
        print(cls.colorize(inputC=input, pcolor="\033[93m"))
        return
    @classmethod
    def FAIL(cls, input):
        print(cls.colorize(inputC=input, pcolor="\033[91m"))
        return
    @classmethod
    def BOLD(cls, input):
        print(cls.colorize(inputC=input, pcolor="\033[1m"))
        return
    @classmethod
    def UNDERLINE(cls, input):
        print(cls.colorize(inputC=input, pcolor="\033[4m"))
        return