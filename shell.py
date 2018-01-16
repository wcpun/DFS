import cmd

class CLI(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.current_path = ''
        self.prompt = "FYP >>> "

    def do_hi(self, arg):
        print("Hello World.")

def main():
    term = CLI()
    term.cmdloop()


if __name__ == '__main__':
    main()
