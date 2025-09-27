#!/usr/bin/env python3
import sys
import tkinter as tk
from tkinter import scrolledtext
import time
import threading

from parser import CommandParser
from commands import CommandExecutor
from vfs import VFS
from logger import XMLLogger
from config import Config

class VFSEmulator:
    def __init__(self):
        self.config = Config().parse_args()
        
        self.vfs = VFS()
        self.logger = XMLLogger(self.config.log_path)
        self.parser = CommandParser()
        self.executor = CommandExecutor(self.vfs, self.logger)
        
        if self.config.vfs_path:
            self.vfs.load_from_json(self.config.vfs_path)
            
        self.root = tk.Tk()
        self.root.title("VFS Emulator - Virtual File System")
        self.root.geometry("800x600")
        
        self.setup_gui()
        
        if self.config.script_path:
            self.root.after(100, lambda: self.execute_script(self.config.script_path))
        
    def setup_gui(self):
        # Output area
        self.output_area = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, width=80, height=25,
            font=("Courier New", 10), bg="black", fg="white"
        )
        self.output_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Input frame
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.prompt_label = tk.Label(self.input_frame, text="$ ", font=("Courier New", 10), fg="green")
        self.prompt_label.pack(side=tk.LEFT)
        
        self.input_entry = tk.Entry(self.input_frame, width=70, font=("Courier New", 10))
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.bind('<Return>', self.execute_command)
        self.input_entry.focus_set()
        
        self.output_area.config(state=tk.DISABLED)
        
        # Welcome message
        self.display_output("=== VFS Emulator ===\n")
        self.display_output("Type 'help' for available commands\n")
        self.display_output(f"Current directory: {self.vfs.current_dir.get_path()}\n\n")
        
    def execute_command(self, event=None, command_text=None):
        if command_text is None:
            command_text = self.input_entry.get()
            self.input_entry.delete(0, tk.END)
        
        self.display_output(f"$ {command_text}\n")
        
        try:
            command, args = self.parser.parse(command_text)
            if command == "exit":
                self.root.quit()
                return
                
            result = self.executor.execute(command, args)
            self.display_output(result + "\n\n")
        except Exception as e:
            self.display_output(f"Error: {str(e)}\n\n")
            
    def execute_script(self, script_path):
        def run_script():
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.root.after(0, lambda l=line: self.execute_command(command_text=l))
                        time.sleep(0.3)
                        
            except Exception as e:
                self.root.after(0, lambda: self.display_output(f"Script error: {str(e)}\n"))
                
        threading.Thread(target=run_script, daemon=True).start()
            
    def display_output(self, text):
        self.output_area.config(state=tk.NORMAL)
        self.output_area.insert(tk.END, text)
        self.output_area.see(tk.END)
        self.output_area.config(state=tk.DISABLED)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    emulator = VFSEmulator()
    emulator.run()