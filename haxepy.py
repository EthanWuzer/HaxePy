import sys
import os
import argparse
from errorHandler import ErrorHandler
from scanner import Scanner

#a haxe interpreter written in python
class haxe:
    def __init__(self):
        self.errorHandler = ErrorHandler()
        
    def run_file(self, path):
        with open(path, "r") as f:
            source = f.read()
        self.run(source)
        if self.errorHandler.hadError:
            sys.exit()
        if self.errorHandler.hadRuntimeError:
            sys.exit()
        return 0

    def run_prompt(self):
        try:
            while True:
                self.run(input("haxe> "))
                self.error_handeler.hadError = False
                self.error_handeler.hadRuntimeError = False
        except KeyboardInterrupt:
            print("\n")

    def run(self, source):
        scanner = Scanner(self.errorHandler(), source)
        tokens = scanner.scanTokens()
        
if __name__ == "__main__":
    haxe = haxe()
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("script", nargs="?", default=None, help="The script to  run")
    args = arg_parser.parse_args()
    if args.script is not None:
        haxe.run_script(args.script)    #run the script
    else:
        haxe.run_prompt()         #run the prompt