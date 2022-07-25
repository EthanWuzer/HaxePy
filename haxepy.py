import sys
import os
import argparse
from errorHandler import ErrorHandler
from scanner import Scanner
from runMode import RunMode as mode
from parser import Parser
from interpreter import Interpreter
# a haxe interpreter written in python


class haxe:
    def __init__(self):
        self.errorHandler = ErrorHandler()
        self.interpreter = Interpreter(self.errorHandler)

    def run_file(self, path):
        with open(path, 'r') as file:
            self.run("".join(file.readlines()), mode.FILE)
            if self.errorHandler.had_error:
                return 1

    def run_prompt(self):
        try:
            while True:
                self.run(input("haxe> "), mode.REPL)
                self.errorHandler.had_error = False
                self.errorHandler.had_runtime_error = False
        except KeyboardInterrupt:
            print("\n")

    def run(self, source, mode):
        scanner = Scanner(self.errorHandler, source)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens, self.errorHandler)
        statements = parser.parse()
        if self.errorHandler.had_error:
            return
        self.interpreter.interpret(statements, mode)


if __name__ == "__main__":
    haxe = haxe()
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("script", nargs="?",
                            default=None, help="The script to  run")
    args = arg_parser.parse_args()
    if args.script is not None:
        haxe.run_file(args.script)  # run the script
    else:
        haxe.run_prompt()  # run the prompt
