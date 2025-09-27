import os
from datetime import datetime

class CommandExecutor:
    def __init__(self, vfs, logger):
        self.vfs = vfs
        self.logger = logger
        
    def execute(self, command, args):
        try:
            if command == "exit":
                result = "Exiting VFS emulator"
            elif command == "ls":
                result = self._ls(args)
            elif command == "cd":
                result = self._cd(args)
            elif command == "date":
                result = self._date(args)
            elif command == "du":
                result = self._du(args)
            elif command == "pwd":
                result = self._pwd(args)
            elif command == "echo":
                result = self._echo(args)
            elif command == "chown":
                result = self._chown(args)
            elif command == "mv":
                result = self._mv(args)
            elif command == "help":
                result = self._help(args)
            else:
                raise ValueError(f"Unknown command: {command}")
                
            self.logger.log_command(command, args, success=True)
            return result
            
        except Exception as e:
            self.logger.log_command(command, args, success=False, message=str(e))
            return f"Error: {str(e)}"
            
    def _ls(self, args):
        detailed = '-l' in args or '-la' in args
        show_all = '-a' in args or '-la' in args
        
        # Фильтруем путь из аргументов
        path_args = [arg for arg in args if not arg.startswith('-')]
        path = path_args[0] if path_args else "."
        
        items = self.vfs.list_directory(path)
        if items is None:
            raise ValueError(f"Directory not found: {path}")
            
        if not items:
            return ""
            
        if detailed:
            result = []
            # Добавляем текущую и родительскую директории для -a
            if show_all:
                result.append(f"drwxr-xr-x {self.vfs.current_dir.owner:>8} {0:>8} .")
                if self.vfs.current_dir.parent:
                    result.append(f"drwxr-xr-x {self.vfs.current_dir.parent.owner:>8} {0:>8} ..")
            
            for item in items:
                if not show_all and item['name'].startswith('.'):
                    continue
                perm = item['permissions']
                owner = item['owner']
                size = item['size']
                name = item['name']
                type_char = '-' if item['type'] == 'file' else 'd'
                result.append(f"{type_char}{perm} {owner:>8} {size:>8} {name}")
            return "\n".join(result)
        else:
            names = [item['name'] for item in items 
                    if show_all or not item['name'].startswith('.')]
            return " ".join(names)
            
    def _cd(self, args):
        if not args:
            path = "/"
        else:
            path = args[0]
            
        if self.vfs.change_directory(path):
            return f"Changed to directory: {self.vfs.current_dir.get_path()}"
        else:
            raise ValueError(f"Directory not found: {path}")
            
    def _date(self, args):
        format_str = args[0] if args else "%Y-%m-%d %H:%M:%S"
        return datetime.now().strftime(format_str)
        
    def _du(self, args):
        path = args[0] if args else "."
        target_node = self.vfs._find_node(path) if path != "." else self.vfs.current_dir
        
        if not target_node:
            raise ValueError(f"Path not found: {path}")
            
        total_size = self.vfs.calculate_size(target_node)
        human_readable = self._human_readable_size(total_size)
        return f"{total_size}\t{path}\t({human_readable})"
        
    def _human_readable_size(self, size):
        for unit in ['B', 'K', 'M', 'G']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}T"
        
    def _pwd(self, args):
        return self.vfs.current_dir.get_path()
        
    def _echo(self, args):
        return " ".join(args)
        
    def _chown(self, args):
        if len(args) < 2:
            raise ValueError("Usage: chown OWNER FILE")
            
        owner = args[0]
        path = args[1]
        
        node = self.vfs._find_node(path)
        if not node:
            raise ValueError(f"File not found: {path}")
            
        old_owner = node.owner
        node.owner = owner
        return f"Changed owner of {path} from {old_owner} to {owner}"
        
    def _mv(self, args):
        if len(args) < 2:
            raise ValueError("Usage: mv SOURCE DEST")
            
        source_path = args[0]
        dest_path = args[1]
        
        source_node = self.vfs._find_node(source_path)
        if not source_node:
            raise ValueError(f"Source not found: {source_path}")
            
        source_parent = source_node.parent
        source_name = source_node.name
        
        if "/" in dest_path:
            dest_parts = dest_path.rstrip("/").split("/")
            dest_name = dest_parts[-1]
            dest_parent_path = "/".join(dest_parts[:-1]) if len(dest_parts) > 1 else "/"
            dest_parent = self.vfs._find_node(dest_parent_path)
        else:
            dest_name = dest_path
            dest_parent = self.vfs.current_dir
            
        if not dest_parent or dest_parent.is_file:
            raise ValueError(f"Invalid destination: {dest_path}")
            
        if dest_name in dest_parent.children:
            raise ValueError(f"Destination already exists: {dest_path}")
            
        del source_parent.children[source_name]
        source_node.name = dest_name
        dest_parent.add_child(source_node)
        
        return f"Moved {source_path} to {dest_path}"
        
    def _help(self, args):
        help_text = """Available commands:
ls [OPTIONS] [PATH]    - List directory contents
cd [PATH]              - Change directory  
pwd                    - Print working directory
date [FORMAT]          - Show current date and time
du [PATH]              - Show disk usage
chown OWNER FILE       - Change file owner
mv SOURCE DEST         - Move or rename files
echo [TEXT]            - Display text
exit                   - Exit the emulator
help                   - Show this help message

Options:
ls -l                  - Detailed listing
ls -a                  - Show hidden files
ls -la                 - Detailed listing with hidden files

Examples:
ls -la                 # Detailed listing with hidden files
cd /home/user          # Change to absolute path
chown user file.txt    # Change owner
mv old.txt new.txt     # Rename file
date "+%Y-%m-%d"       # Custom date format"""
        return help_text