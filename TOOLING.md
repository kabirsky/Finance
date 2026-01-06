# Python Tooling Guide

For JS/C++ developers getting started with Python.

## Running Python

### Basic execution
```bash
# Run a script
python script.py
# or on some systems
python3 script.py

# Run with module syntax (uses package structure)
python -m bank_converter

# Interactive REPL (like Node.js REPL)
python
>>> print("Hello")
Hello
>>> exit()
```

### Which Python?
```bash
# Check version
python --version
# Python 3.11.0

# On Windows, you might have 'py' launcher
py --version
py -3.11 script.py  # Use specific version
```

---

## Package Management (pip = npm)

### Basic commands
```bash
# Install a package (like: npm install lodash)
pip install requests

# Install specific version
pip install requests==2.28.0
pip install "requests>=2.0,<3.0"

# Uninstall
pip uninstall requests

# List installed packages
pip list

# Show package info
pip show requests
```

### requirements.txt = package.json
```bash
# Install all dependencies (like: npm install)
pip install -r requirements.txt

# Generate requirements from current environment
pip freeze > requirements.txt
```

**requirements.txt format:**
```
requests==2.28.0
pandas>=1.5.0
openpyxl>=3.1.0
# Comments start with #
```

**Comparison:**
| npm | pip |
|-----|-----|
| `npm install` | `pip install -r requirements.txt` |
| `npm install pkg` | `pip install pkg` |
| `npm uninstall pkg` | `pip uninstall pkg` |
| `npm list` | `pip list` |
| `package.json` | `requirements.txt` |
| `package-lock.json` | `requirements.txt` (no separate lock) |

---

## Virtual Environments (venv)

### Why?
Like `node_modules`, but for Python. Without venv, packages install globally and can conflict between projects.

### Creating and using venv

```bash
# Create a virtual environment (like: npm init, but for isolation)
python -m venv venv
# Creates a 'venv' folder with isolated Python

# Activate it (IMPORTANT - do this before installing packages!)

# Windows (Command Prompt)
venv\Scripts\activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# macOS/Linux
source venv/bin/activate

# Your prompt changes to show (venv):
(venv) C:\project>

# Now pip installs packages ONLY in this venv
pip install requests

# Deactivate when done
deactivate
```

### Best practices
```bash
# 1. Create venv in project root
python -m venv venv

# 2. Add to .gitignore (don't commit it!)
# venv/

# 3. Activate before working
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. If you add new packages, update requirements
pip freeze > requirements.txt
```

---

## Project Structure

### Python packages
```
my_project/
├── my_package/           # Package = folder with __init__.py
│   ├── __init__.py       # Makes this folder a package (can be empty)
│   ├── module1.py        # Module = .py file
│   ├── module2.py
│   └── subpackage/       # Nested package
│       ├── __init__.py
│       └── utils.py
├── tests/
│   └── test_module1.py
├── requirements.txt
└── main.py               # Entry point
```

### `__init__.py` explained
```python
# my_package/__init__.py

# Can be empty! Just marks folder as package.

# Or can define what's exported:
from .module1 import MyClass
from .module2 import helper_function

# Now users can do:
# from my_package import MyClass, helper_function
```

### Import system
```python
# Absolute imports (preferred)
from my_package.module1 import MyClass
from my_package.subpackage.utils import helper

# Relative imports (within same package)
from .module1 import MyClass           # Same folder
from ..other_package import something  # Parent folder

# The dot notation:
# .  = current package
# .. = parent package
```

**Comparison to JS/C++:**
| Python | JavaScript | C++ |
|--------|------------|-----|
| `from x import y` | `import { y } from 'x'` | `#include` + using |
| `import x` | `import * as x from 'x'` | `#include` |
| `__init__.py` | `index.js` | Header files |
| Package (folder) | Module (folder) | Namespace |
| Module (.py) | Module (.js) | Translation unit |

---

## `__pycache__` - What is it?

```
my_project/
├── my_module.py
└── __pycache__/
    └── my_module.cpython-311.pyc   # Compiled bytecode
```

- Python compiles `.py` to bytecode (`.pyc`) for faster loading
- Created automatically when you import a module
- **Always gitignore it!** Add `__pycache__/` to `.gitignore`
- Safe to delete (recreated automatically)
- Like `.class` files in Java or incremental build caches

---

## Type Checking with mypy

Python's type hints are NOT enforced at runtime. For static checking, use `mypy`:

```bash
# Install
pip install mypy

# Check a file
mypy my_module.py

# Check entire project
mypy .
```

**Example:**
```python
# my_module.py
def greet(name: str) -> str:
    return f"Hello {name}"

greet(123)  # Python runs this fine!
            # But mypy will catch it:
            # error: Argument 1 has incompatible type "int"; expected "str"
```

### Common type hints
```python
from typing import List, Dict, Optional, Tuple, Union, Any

# Basic types
x: int = 5
y: float = 3.14
z: str = "hello"
flag: bool = True

# Collections
items: list[int] = [1, 2, 3]              # Python 3.9+
items: List[int] = [1, 2, 3]              # Older Python
mapping: dict[str, int] = {"a": 1}        # Python 3.9+
mapping: Dict[str, int] = {"a": 1}        # Older Python

# Optional = can be None
name: Optional[str] = None                 # str or None

# Union = multiple types
value: Union[int, str] = 5                 # int or str
value: int | str = 5                       # Python 3.10+ syntax

# Tuple with specific types
point: tuple[int, int] = (10, 20)

# Any = disable type checking
data: Any = something_unknown()

# Function types
from typing import Callable
handler: Callable[[int, str], bool]        # (int, str) -> bool
```

---

## Testing with pytest

```bash
# Install
pip install pytest

# Run all tests
pytest

# Run specific file
pytest tests/test_module.py

# Run with verbose output
pytest -v

# Run tests matching a pattern
pytest -k "test_login"
```

**Test file structure:**
```python
# tests/test_calculator.py

from my_package.calculator import add, subtract

def test_add():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, 1) == 0

def test_subtract():
    assert subtract(5, 3) == 2

# Tests are functions starting with "test_"
# Use assert for checks (no special assertion library needed)
```

---

## Linting and Formatting

### Black (formatter - like Prettier)
```bash
pip install black

# Format a file
black my_module.py

# Format entire project
black .

# Check without modifying
black --check .
```

### Ruff (linter - fast, like ESLint)
```bash
pip install ruff

# Lint
ruff check .

# Fix auto-fixable issues
ruff check --fix .
```

### isort (import sorter)
```bash
pip install isort

# Sort imports
isort .
```

### All-in-one setup
```bash
pip install black ruff isort

# Add to requirements-dev.txt for dev dependencies
```

---

## Debugging

### Print debugging (quick and dirty)
```python
print(f"DEBUG: x = {x}")
print(f"DEBUG: type = {type(x)}")

# Pretty print complex objects
from pprint import pprint
pprint(complex_dict)
```

### breakpoint() - built-in debugger
```python
def my_function():
    x = calculate_something()
    breakpoint()  # Drops into debugger here!
    return x

# In debugger:
# n - next line
# s - step into function
# c - continue
# p variable - print variable
# q - quit
```

### VS Code debugging
1. Install Python extension
2. Create `.vscode/launch.json`:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "${file}",
            "console": "integratedTerminal"
        }
    ]
}
```
3. Set breakpoints by clicking left of line numbers
4. Press F5 to debug

---

## Common File Structure for a Project

```
my_project/
├── .gitignore
├── README.md
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Dev dependencies (pytest, black, etc.)
├── setup.py                  # For installable packages (optional)
├── pyproject.toml            # Modern config (replaces setup.py)
│
├── src/                      # Or just put package at root
│   └── my_package/
│       ├── __init__.py
│       └── ...
│
├── tests/
│   ├── __init__.py
│   └── test_*.py
│
└── venv/                     # Virtual environment (gitignored)
```

---

## Quick Command Reference

| Task | Command |
|------|---------|
| Run script | `python script.py` |
| Create venv | `python -m venv venv` |
| Activate venv (Windows) | `venv\Scripts\activate` |
| Install dependencies | `pip install -r requirements.txt` |
| Install package | `pip install package_name` |
| Save dependencies | `pip freeze > requirements.txt` |
| Run tests | `pytest` |
| Format code | `black .` |
| Lint code | `ruff check .` |
| Type check | `mypy .` |
| Interactive Python | `python` (then `exit()` to quit) |
