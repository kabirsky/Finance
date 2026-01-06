#!/usr/bin/env python3
"""
Run the Bank to Budget Converter application.

=== LEARNING: This file demonstrates ===
- The shebang line (#!/usr/bin/env python3)
- The `if __name__ == "__main__":` pattern
- sys.path manipulation for imports
- Script vs module execution

=== LEARNING: Why have a separate entry point file? ===
This file exists to:
1. Provide a clean entry point that works from any directory
2. Avoid import issues with relative imports in packages
3. Set up the Python path properly before importing the main module

[C++] Like having a main.cpp that only contains main() and calls App::run()
"""

# =============================================================================
# SHEBANG LINE
# =============================================================================
# The first line #!/usr/bin/env python3 is a "shebang" (hash-bang).
# On Unix/Linux/Mac, it tells the system which interpreter to use.
#
# [C++] No equivalent - C++ is compiled, not interpreted
#
# #!/usr/bin/env python3 means:
# "Find python3 in the user's PATH and use it to run this script"
#
# This allows running the script directly:
#   ./run_converter.py     (on Unix, after chmod +x)
#   python run_converter.py (on any system)

# =============================================================================
# IMPORTS
# =============================================================================
import sys                # System-specific parameters and functions
from pathlib import Path  # Object-oriented path handling

# === LEARNING: sys.path manipulation ===
# sys.path is a list of directories where Python looks for modules.
# We add the project root so Python can find our 'bank_converter' package.
#
# [C++] Like adding directories to the include path (-I flag)
#
# __file__ is a special variable containing the path to THIS script.
# Path(__file__).parent gives us the directory containing this script.
#
# sys.path.insert(0, ...) adds at the BEGINNING of the search path,
# ensuring our package is found before any system packages with the same name.
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# === LEARNING: Absolute vs Relative Imports ===
# Now that sys.path is set up, we can use an ABSOLUTE import.
# "from bank_converter.gui.app" starts from our package root.
#
# [C++] Like: #include "bank_converter/gui/app.h"
#
# This is different from the RELATIVE imports inside the package
# (like "from ..core.reader import ...") which only work inside packages.
from bank_converter.gui.app import BankConverterApp


# =============================================================================
# ENTRY POINT
# =============================================================================
# === LEARNING: if __name__ == "__main__": ===
# This is Python's idiom for "main function".
#
# When a Python file is:
# - Run directly: __name__ == "__main__"
# - Imported as module: __name__ == module name (e.g., "run_converter")
#
# [C++] Like having:
#       #ifdef MAIN_FILE
#       int main() { ... }
#       #endif
#
# WHY is this useful?
# 1. Allows the file to be both a script AND an importable module
# 2. Prevents code from running when file is just imported
# 3. Standard pattern that other developers expect
#
# Example:
#   python run_converter.py     -> __name__ == "__main__" (runs app)
#   from run_converter import X -> __name__ == "run_converter" (doesn't run app)

if __name__ == "__main__":
    # === LEARNING: Command-line arguments with sys.argv ===
    # sys.argv is a list of command-line arguments:
    # - sys.argv[0] = script name (run_converter.py)
    # - sys.argv[1] = first argument (file path if dragged onto script)
    # - sys.argv[2:] = additional arguments
    #
    # [C++] Like: int main(int argc, char* argv[])
    #
    # When you drag a file onto a .py script in Windows:
    # - Windows runs: python.exe run_converter.py "C:\path\to\file.csv"
    # - sys.argv becomes ['run_converter.py', 'C:\\path\\to\\file.csv']

    # Get initial file from command line if provided
    initial_file = None
    if len(sys.argv) > 1:
        # === LEARNING: Path validation ===
        # Check if the argument is an existing file before using it
        potential_file = Path(sys.argv[1])
        if potential_file.exists() and potential_file.is_file():
            initial_file = str(potential_file)

    # Create the application instance with optional initial file
    app = BankConverterApp(initial_file=initial_file)

    # Start the event loop (this blocks until window closes)
    # [C++/Qt] Like: return app.exec();
    app.run()

# === LEARNING: What happens when you run this script ===
# 1. Python executes the file top-to-bottom
# 2. imports are resolved (sys.path is set, then bank_converter imported)
# 3. if __name__ == "__main__" evaluates to True (since we ran directly)
# 4. Command-line args are parsed (sys.argv[1] = dropped file path)
# 5. BankConverterApp(initial_file) creates the window
# 6. app.run() loads the initial file if provided, then starts mainloop()
# 7. Script ends after run() returns

# === LEARNING: Drag-and-drop onto .py file (Windows) ===
# To enable dragging files onto run_converter.py:
# 1. Right-click run_converter.py -> Properties -> Opens with -> python.exe
# 2. Or create a .bat file that runs: python "%~dp0run_converter.py" %*
# 3. Or associate .py files with pythonw.exe (no console window)
#
# When you drag file.csv onto run_converter.py:
# Windows executes: python.exe run_converter.py "C:\full\path\to\file.csv"
