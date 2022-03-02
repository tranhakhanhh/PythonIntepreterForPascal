class Scanner():
    cfg = {}
    scan_string = ""
    start = 0

    def __init__(self, contextFree):
        self.cfg = contextFree
        self.scan_string = ""
        self.start = 0

    def startScan(self, scanS):
        self.scan_string = scanS
        self.start = 0

    def nextToken(self):
        token = ""
        value = ""
        while self.start < len(self.scan_string):
            while self.scan_string[self.start].isspace():
                self.start = self.start + 1
            curr_char = self.scan_string[self.start]
            if curr_char in ['(', ')', '+', '-', '*', '/', ';', '.', '=', '>', '<', ',', '[', ']']:
                token = curr_char
                value = token
            elif curr_char == ':':
                self.start = self.start + 1
                try:
                    next_char = self.scan_string[self.start]
                except IndexError:
                    raise Exception("Invalid token")
                if next_char == "=":
                    token = ":="
                    value = token
                else:
                    self.start = self.start - 1
                    token = ":"
                    value = token
            elif curr_char.isdigit():
                token = curr_char
                while self.start + 1 < len(self.scan_string) and self.scan_string[self.start + 1].isdigit():
                    token = token + self.scan_string[self.start + 1]
                    self.start = self.start + 1
                value = token
                token = "number"
            elif curr_char.isalpha():
                token = curr_char
                # only allow variable [A-Za-z0-9] and _
                # if token is function/variable name
                while self.start + 1 < len(self.scan_string) and (self.scan_string[self.start + 1].isalpha() or self.scan_string[self.start + 1].isdigit() or self.scan_string[
                    self.start + 1] == '_'):
                    token = token + self.scan_string[self.start + 1]
                    self.start = self.start + 1
                value = token
                #####Since in Pascal, keywords are not case-sensitive
                if token.lower() not in ["begin", "end", "var", "program", "function", "for", "to", "do", "if", "then",
                                         "else", "repeat", "until"]:
                    token = "id"
                else:
                  value = token.lower()
            elif curr_char == "'":
                token = curr_char
                while self.start + 1 < len(self.scan_string) and self.scan_string[self.start + 1] != "'":
                    token = token + self.scan_string[self.start + 1]
                    self.start = self.start + 1
                if self.scan_string[self.start + 1] == "'":  # if the loop ends because string was closed
                    value = token + "'"
                    token = "string"
                    self.start = self.start + 1
                else:
                    raise Exception("Invalid token")
            else:
                raise Exception("Invalid token")
            self.start = self.start + 1
            print("CURR TOKEN "+ value)
            return value
        return "$$"


# testing the scanner
if __name__ == "__main__":
    example_object = open("example3.txt")
    example = example_object.read()
    cfg = {}
    myScanner = Scanner(cfg)
    myScanner.startScan(example)
    t = myScanner.nextToken()
    while t != "$$":
      t = myScanner.nextToken()
    print("SUCCESS")
    example_object.close()