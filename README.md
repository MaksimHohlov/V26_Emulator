# VFS Emulator

Эмулятор командной строки UNIX-подобной ОС с виртуальной файловой системой.

## Функциональность

- **REPL интерфейс** с графическим GUI
- **Виртуальная файловая система** на основе JSON
- **XML логирование** всех операций
- **Поддержка скриптов** для автоматического тестирования
- **Полная имитация** UNIX командной строки

## Установка и запуск

```bash
# Клонирование репозитория
git clone <repository>
cd vfs_emulator

# Запуск в интерактивном режиме
python src/main.py

# Запуск с VFS и скриптом
python src/main.py --vfs-path vfs_examples/multi_level.json --script scripts/final_test.txt

# Запуск с логгированием
python src/main.py --log-path logs/my_session.log