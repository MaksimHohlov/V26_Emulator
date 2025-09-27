#!/usr/bin/env python3
from parser import CommandParser

def test_parser():
    parser = CommandParser()
    
    # Тест простой команды
    command, args = parser.parse("ls")
    assert command == "ls"
    assert args == []
    
    # Тест команды с аргументами
    command, args = parser.parse("cd /home/user")
    assert command == "cd"
    assert args == ["/home/user"]
    
    # Тест кавычек
    command, args = parser.parse('echo "hello world"')
    assert command == "echo"
    assert args == ["hello world"]
    
    print("All parser tests passed!")

if __name__ == "__main__":
    test_parser()