import argparse
import os
import sys

class Config:
    def __init__(self):
        self.vfs_path = None
        self.log_path = "vfs.log"
        self.script_path = None
        
    def parse_args(self):
        parser = argparse.ArgumentParser(description="VFS Emulator")
        parser.add_argument("--vfs-path", help="Path to VFS JSON file")
        parser.add_argument("--log-path", default="vfs.log", help="Path to log file")
        parser.add_argument("--script", help="Path to startup script")
        
        args = parser.parse_args()
        
        # Отладочный вывод параметров
        print("=== VFS Emulator Configuration ===")
        print(f"VFS Path: {args.vfs_path}")
        print(f"Log Path: {args.log_path}")
        print(f"Script Path: {args.script}")
        print("==================================")
        
        if args.vfs_path:
            if not os.path.exists(args.vfs_path):
                print(f"Error: VFS file not found: {args.vfs_path}")
                sys.exit(1)
            self.vfs_path = os.path.abspath(args.vfs_path)
            
        self.log_path = os.path.abspath(args.log_path)
        
        if args.script:
            if not os.path.exists(args.script):
                print(f"Error: Script file not found: {args.script}")
                sys.exit(1)
            self.script_path = os.path.abspath(args.script)
            
        return self