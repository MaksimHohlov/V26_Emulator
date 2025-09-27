import shlex

class CommandParser:
    def parse(self, input_text):
        if not input_text.strip():
            raise ValueError("Empty command")
            
        try:
            parts = shlex.split(input_text)
            command = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            return command, args
        except ValueError as e:
            raise ValueError(f"Parse error: {str(e)}")