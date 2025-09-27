import json
import base64
from pathlib import Path

class VFSNode:
    def __init__(self, name, is_file=False, content="", owner="user", permissions="rw-r--r--"):
        self.name = name
        self.is_file = is_file
        self.content = content
        self.owner = owner
        self.permissions = permissions
        self.children = {}
        self.parent = None
        
    def add_child(self, node):
        node.parent = self
        self.children[node.name] = node
        
    def get_child(self, name):
        return self.children.get(name)
    
    def get_path(self):
        path_parts = []
        current = self
        while current and current.name:
            path_parts.insert(0, current.name)
            current = current.parent
        return "/" + "/".join(path_parts) if path_parts else "/"

class VFS:
    def __init__(self):
        self.root = VFSNode("")
        self.current_dir = self.root
        self._create_sample_structure()  # ДОБАВЛЕНО: создаем тестовые данные
        
    def _create_sample_structure(self):
        """Создает тестовую структуру файлов по умолчанию"""
        # Создаем папки
        home_dir = VFSNode("home", is_file=False, permissions="rwxr-xr-x")
        user_dir = VFSNode("user", is_file=False, permissions="rwxr-xr-x")
        documents_dir = VFSNode("documents", is_file=False, permissions="rwxr-xr-x")
        etc_dir = VFSNode("etc", is_file=False, permissions="rwxr-xr-x")
        
        # Создаем файлы
        file1 = VFSNode("file1.txt", is_file=True, content="Hello World!", owner="user")
        file2 = VFSNode("file2.txt", is_file=True, content="Another file", owner="user")
        hidden_file = VFSNode(".bashrc", is_file=True, content="export PS1", owner="user")
        config_file = VFSNode("config.conf", is_file=True, content="setting=value", owner="root")
        readme_file = VFSNode("README.md", is_file=True, content="# Project", owner="user")
        
        # Строим иерархию
        self.root.add_child(home_dir)
        self.root.add_child(etc_dir)
        
        home_dir.add_child(user_dir)
        etc_dir.add_child(config_file)
        
        user_dir.add_child(documents_dir)
        user_dir.add_child(hidden_file)
        user_dir.add_child(readme_file)
        
        documents_dir.add_child(file1)
        documents_dir.add_child(file2)
        
        self.current_dir = self.root
        
    def load_from_json(self, json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        self.root = self._build_tree(data, None)
        self.current_dir = self.root
        print(f"VFS loaded from {json_path}")
        
    def _build_tree(self, data, parent):
        if data["type"] == "file":
            content = base64.b64decode(data.get("content", "")).decode('utf-8') if data.get("content") else ""
            node = VFSNode(
                data["name"], 
                is_file=True, 
                content=content,
                owner=data.get("owner", "user"),
                permissions=data.get("permissions", "rw-r--r--")
            )
        else:
            node = VFSNode(
                data["name"],
                is_file=False,
                owner=data.get("owner", "user"),
                permissions=data.get("permissions", "rwxr-xr-x")
            )
            for child_data in data.get("children", []):
                child_node = self._build_tree(child_data, node)
                node.add_child(child_node)
                
        if parent:
            parent.add_child(node)
            
        return node
    
    def change_directory(self, path):
        if path == "/" or path == "":
            self.current_dir = self.root
            return True
            
        if path.startswith("/"):
            target_dir = self.root
            path_parts = [p for p in path[1:].split("/") if p]
        else:
            target_dir = self.current_dir
            path_parts = [p for p in path.split("/") if p]
            
        for part in path_parts:
            if part == "..":
                if target_dir.parent:
                    target_dir = target_dir.parent
            elif part == ".":
                continue
            elif part:
                if part in target_dir.children and not target_dir.children[part].is_file:
                    target_dir = target_dir.children[part]
                else:
                    return False
                    
        self.current_dir = target_dir
        return True
    
    def list_directory(self, path="."):
        if path == ".":
            target_dir = self.current_dir
        elif path == "/":
            target_dir = self.root
        else:
            target_dir = self._find_node(path)
            if not target_dir or target_dir.is_file:
                return None
                
        items = []
        for name, node in target_dir.children.items():
            items.append({
                'name': name,
                'type': 'file' if node.is_file else 'directory',
                'permissions': node.permissions,
                'owner': node.owner,
                'size': len(node.content) if node.is_file else 0
            })
            
        return items
    
    def _find_node(self, path):
        if path == "/":
            return self.root
            
        if path.startswith("/"):
            current = self.root
            path_parts = [p for p in path[1:].split("/") if p]
        else:
            current = self.current_dir
            path_parts = [p for p in path.split("/") if p]
            
        for part in path_parts:
            if part == "..":
                if current.parent:
                    current = current.parent
            elif part == ".":
                continue
            elif part and part in current.children:
                current = current.children[part]
            else:
                return None
        return current
    
    def calculate_size(self, node=None):
        if node is None:
            node = self.current_dir
            
        if node.is_file:
            return len(node.content)
        else:
            total = 0
            for child in node.children.values():
                total += self.calculate_size(child)
            return total
        