import xml.etree.ElementTree as ET
from datetime import datetime
import os

class XMLLogger:
    def __init__(self, log_path):
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path) if os.path.dirname(log_path) else '.', exist_ok=True)
        self.root = ET.Element("vfs_log")
        
    def log_command(self, command, args, success=True, message=""):
        event = ET.SubElement(self.root, "event")
        
        timestamp = ET.SubElement(event, "timestamp")
        timestamp.text = datetime.now().isoformat()
        
        cmd_elem = ET.SubElement(event, "command")
        cmd_elem.text = command
        
        args_elem = ET.SubElement(event, "arguments")
        args_elem.text = str(args)
        
        status = ET.SubElement(event, "status")
        status.text = "success" if success else "error"
        
        if message:
            msg_elem = ET.SubElement(event, "message")
            msg_elem.text = message
            
        self._save_log()
        
    def _save_log(self):
        try:
            tree = ET.ElementTree(self.root)
            with open(self.log_path, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                tree.write(f, encoding='unicode', method='xml')
        except Exception as e:
            print(f"Log save error: {e}")