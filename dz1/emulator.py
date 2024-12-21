import os
import sys
import zipfile
import io
import subprocess
from pathlib import Path

class ShellEmulator:
    def __init__(self, hostname, zip_path, startup_script):
        self.hostname = hostname
        self.zip_path = zip_path
        self.startup_script = startup_script
        self.virtual_fs = {}
        self.current_dir = "/"

        self.load_virtual_fs()

    def load_virtual_fs(self):
        with zipfile.ZipFile(self.zip_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                self.virtual_fs[file_info.filename] = zip_ref.read(file_info.filename)

    def run(self):
        if self.startup_script:
            self.execute_script(self.startup_script)

        while True:
            command = input(f"{self.hostname}:{self.current_dir} $ ")
            if command.strip() == "exit":
                break
            self.execute_command(command)

    def execute_script(self, script_path):
        if script_path in self.virtual_fs:
            script_commands = self.virtual_fs[script_path].decode().splitlines()
            for command in script_commands:
                self.execute_command(command)
        else:
            print(f"Script {script_path} not found.")

    def execute_command(self, command):
        parts = command.split()
        cmd = parts[0]

        if cmd == "ls":
            self.ls()
        elif cmd == "cd":
            self.cd(parts[1] if len(parts) > 1 else "")
        elif cmd == "echo":
            self.echo(parts[1:] if len(parts) > 1 else [])
        elif cmd == "cal":
            self.cal()
        elif cmd == "tac":
            self.tac(parts[1] if len(parts) > 1 else "")
        else:
            print(f"{cmd}: command not found")

    def ls(self):
        for filename in self.virtual_fs.keys():
            if filename.startswith(self.current_dir):
                print(filename)

    def cd(self, path):
        if path == "..":
            self.current_dir = "/".join(self.current_dir.split("/")[:-1]) or "/"
        elif path in self.virtual_fs:
            self.current_dir = path
        else:
            print(f"cd: {path}: No such file or directory")

    def echo(self, args):
        print(" ".join(args))

    def cal(self):
        subprocess.run(["cal"])

    def tac(self, filename):
        if filename in self.virtual_fs:
            content = self.virtual_fs[filename].decode().splitlines()
            for line in reversed(content):
                print(line)
        else:
            print(f"tac: {filename}: No such file")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python shell_emulator.py <hostname> <zip_path> <startup_script>")
        sys.exit(1)

    hostname = sys.argv[1]
    zip_path = sys.argv[2]
    startup_script = sys.argv[3]

    emulator = ShellEmulator(hostname, zip_path, startup_script)
    emulator.run()
