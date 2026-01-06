"""
Main application window.

=== LEARNING: This module demonstrates ===
- Composition pattern (app contains multiple components)
- Event-driven programming with tkinter
- State management with instance variables
- wait_window() for modal dialog handling
- Platform-specific code (os.name checks)
- Drag-and-drop file handling with tkinterdnd2
"""

# =============================================================================
# IMPORTS
# =============================================================================
import tkinter as tk
# === LEARNING: Multiple imports from same module ===
# [C++] Like: #include <tkinter/ttk> + #include <tkinter/filedialog>
from tkinter import ttk, filedialog, messagebox
from typing import List, Optional

# === LEARNING: tkinterdnd2 for drag-and-drop ===
# This library adds drag-and-drop support to tkinter.
# TkinterDnD.Tk() replaces tk.Tk() to enable DnD functionality.
# [C++/Qt] Like QMimeData and dropEvent handling
from tkinterdnd2 import DND_FILES, TkinterDnD

# === LEARNING: Relative imports from parent package ===
# '..' goes up one level, then into 'core' subpackage
# [C++] Like: #include "../core/reader.h"
from ..core.reader import BankFileReader
from ..core.converter import BankConverter
from ..core.writer import BudgetWriter
from ..core.models import BankTransaction, BudgetTransaction, UnknownMapping
from ..config.manager import ConfigManager

# Import from same package (gui)
from .preview_frame import PreviewFrame
from .mapping_dialog import MappingDialog
from .config_dialog import ConfigDialog


class BankConverterApp:
    """
    Main application window.

    === LEARNING: Composition Pattern ===
    This class CONTAINS (has-a) other objects rather than inheriting.
    - self.root = the main window (tk.Tk)
    - self.config = configuration manager
    - self.reader = file reader
    - self.converter = conversion logic
    - self.writer = output writer
    - self.raw_preview, self.converted_preview = UI components

    [C++] This is dependency injection via constructor/composition:
          class BankConverterApp {
              ConfigManager config_;
              BankFileReader reader_;
              BankConverter converter_;
              // ...
          };

    Benefits:
    - Easy to test (can mock dependencies)
    - Clear separation of concerns
    - Components are replaceable
    """

    def __init__(self, initial_file: Optional[str] = None):
        """
        Initialize the application.

        === LEARNING: TkinterDnD.Tk() ===
        TkinterDnD.Tk() creates the ROOT window with drag-and-drop support.
        It replaces tk.Tk() and enables file dropping functionality.

        [C++/Qt] Like: QApplication app; QMainWindow window; with dropEvent

        Args:
            initial_file: Optional path to load on startup (for drag-drop onto .py file
                         or command-line arguments).
        """
        # === LEARNING: TkinterDnD vs tk.Tk ===
        # TkinterDnD.Tk() is a subclass of tk.Tk with DnD capabilities
        # Must use this instead of tk.Tk() for drag-and-drop to work
        self.root = TkinterDnD.Tk()
        self.root.title("Bank to Budget Converter")

        # geometry("WxH") sets window size (Width x Height in pixels)
        self.root.geometry("1000x700")

        # minsize() prevents window from being resized too small
        # [C++/Qt] Like: setMinimumSize(800, 500)
        self.root.minsize(800, 500)

        # === LEARNING: Creating component instances ===
        # Each component is created and stored as an instance variable.
        # Note: Order matters - converter needs config, so config first.
        self.config = ConfigManager()
        self.reader = BankFileReader()
        self.converter = BankConverter(self.config)  # Dependency injection
        self.writer = BudgetWriter()

        # === LEARNING: Instance variables with type hints ===
        # These store the application state.
        # [C++] Like: std::vector<BankTransaction> raw_transactions_;
        self.raw_transactions: List[BankTransaction] = []
        self.converted_transactions: List[BudgetTransaction] = []

        # Store initial file to load after UI is ready
        self._initial_file = initial_file

        # Setup UI (common pattern to separate UI setup from __init__)
        self._setup_styles()
        self._setup_ui()
        self._setup_drag_drop()

    def _setup_styles(self):
        """
        Configure ttk styles.

        === LEARNING: ttk Styles ===
        ttk widgets support "styles" for consistent appearance.
        Style names follow convention: "Name.TWidgetType"

        [C++/Qt] Like Qt stylesheets or QStyle
        """
        style = ttk.Style()
        # Create a style named "Title.TLabel" with bold font
        style.configure("Title.TLabel", font=("TkDefaultFont", 12, "bold"))

    def _setup_drag_drop(self):
        """
        Configure drag-and-drop functionality.

        === LEARNING: tkinterdnd2 drag-and-drop ===
        1. drop_target_register() - marks widget as accepting drops
        2. dnd_bind() - binds drop event to handler
        3. DND_FILES - constant indicating file drop type

        [C++/Qt] Like:
            setAcceptDrops(true);
            void dropEvent(QDropEvent* event) { ... }

        The drop handler receives event.data containing the dropped file path(s).
        On Windows, paths with spaces are wrapped in curly braces: {C:/path with spaces/file.csv}
        """
        # Register the entire root window as a drop target
        # This allows dropping files anywhere in the app window
        self.root.drop_target_register(DND_FILES)

        # Bind the drop event to our handler
        # <<Drop>> is the virtual event fired when files are dropped
        self.root.dnd_bind('<<Drop>>', self._on_file_drop)

    def _on_file_drop(self, event):
        """
        Handle file drop event.

        === LEARNING: Processing dropped file paths ===
        event.data contains the dropped path(s) as a string.
        On Windows, paths with spaces are wrapped in braces: {C:/My Files/data.csv}
        Multiple files are space-separated (but braced paths are kept together).

        [C++/Qt] Like processing QMimeData::urls() in dropEvent

        Args:
            event: Drop event containing file path in event.data
        """
        import re

        # Get the dropped data (file path)
        raw_data = event.data.strip()

        # === LEARNING: Parsing tkinterdnd2 file paths ===
        # tkinterdnd2 returns paths in a special format:
        # - Single file without spaces: C:/path/file.csv
        # - Single file with spaces: {C:/path with spaces/file.csv}
        # - Multiple files: {C:/file one.csv} {C:/file two.csv}
        # - Multiple files without spaces: C:/file1.csv C:/file2.csv
        #
        # We use regex to extract paths properly

        # Pattern matches either {braced paths} or non-space sequences
        # [C++] Like: std::regex pattern(R"(\{[^}]+\}|[^\s]+)")
        pattern = r'\{[^}]+\}|[^\s]+'
        matches = re.findall(pattern, raw_data)

        if not matches:
            return

        # Take the first file path
        path = matches[0]

        # Remove braces if present
        if path.startswith('{') and path.endswith('}'):
            path = path[1:-1]

        # Validate file extension
        if path.lower().endswith(('.csv', '.xlsx')):
            self.file_path_var.set(path)
            self._load_file(path)
        else:
            messagebox.showwarning(
                "Неподдерживаемый файл",
                f"Пожалуйста, перетащите CSV или XLSX файл.\n\nПолучено: {path}"
            )

    def _setup_ui(self):
        """
        Create main UI layout.

        === LEARNING: Grid Geometry Manager ===
        The main layout uses grid() for row/column positioning.

        weight=1 in columnconfigure/rowconfigure means:
        "This row/column should expand when window is resized"

        [C++/Qt] Similar to QGridLayout with stretch factors
        """
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # === LEARNING: Grid weight configuration ===
        # Configure weights for the root window's grid
        self.root.columnconfigure(0, weight=1)  # Column 0 expands
        self.root.rowconfigure(0, weight=1)     # Row 0 expands

        # Configure weights for main_frame's grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)  # Preview section (row 2) expands

        # Create UI sections (split into methods for organization)
        # Row 0: File selection
        self._create_file_section(main_frame)
        # Row 1: Settings
        self._create_settings_section(main_frame)
        # Row 2: Preview tabs (expands)
        self._create_preview_section(main_frame)
        # Row 3: Action buttons
        self._create_action_section(main_frame)

    def _create_file_section(self, parent):
        """
        Create file selection area.

        === LEARNING: LabelFrame ===
        LabelFrame is a Frame with a visible border and title label.
        [C++/Qt] Like QGroupBox
        """
        frame = ttk.LabelFrame(parent, text="Входной файл", padding="10")
        frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame.columnconfigure(1, weight=1)  # Entry expands

        ttk.Label(frame, text="Файл:").grid(row=0, column=0, padx=(0, 10))

        # === LEARNING: StringVar for Entry binding ===
        # StringVar holds the text value - Entry reads/writes to it
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(
            frame, textvariable=self.file_path_var, state="readonly"
        )
        self.file_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        # Button with command callback
        ttk.Button(
            frame, text="Выбрать...", command=self._select_file
        ).grid(row=0, column=2)

    def _create_settings_section(self, parent):
        """Create settings bar."""
        frame = ttk.LabelFrame(parent, text="Настройки", padding="10")
        frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # === LEARNING: pack() geometry manager ===
        # pack() is simpler than grid - widgets stack side by side or top/bottom
        # side="left" means add to the left side of available space
        # [C++/Qt] Like QHBoxLayout for horizontal stacking

        # Owner name entry
        ttk.Label(frame, text="Владелец:").pack(side="left", padx=(0, 5))
        self.owner_var = tk.StringVar(value=self.config.owner)
        owner_entry = ttk.Entry(frame, textvariable=self.owner_var, width=15)
        owner_entry.pack(side="left", padx=(0, 20))

        # Edit config button
        ttk.Button(
            frame,
            text="Редактировать маппинги...",
            command=self._edit_config
        ).pack(side="left", padx=(0, 10))

        # Config file path button
        ttk.Button(
            frame,
            text="Открыть папку конфига",
            command=self._open_config_folder
        ).pack(side="left")

    def _create_preview_section(self, parent):
        """
        Create tabbed preview area.

        === LEARNING: ttk.Notebook ===
        Notebook is a tabbed widget container.
        [C++/Qt] Like QTabWidget
        """
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=2, column=0, sticky="nsew", pady=(0, 10))

        # Raw data preview tab
        # PreviewFrame is our custom component (defined in preview_frame.py)
        self.raw_preview = PreviewFrame(self.notebook, columns=[
            "Дата", "Категория", "Описание", "Сумма", "Статус"
        ])
        self.notebook.add(self.raw_preview, text="Исходные данные")

        # Converted data preview tab
        self.converted_preview = PreviewFrame(self.notebook, columns=[
            "Чей", "Дата", "Сумма", "Назначение", "Тег", "Тип"
        ])
        self.notebook.add(self.converted_preview, text="Результат")

        # Configure row colors for income/expense using tags
        self.converted_preview.configure_tag("income", background="#d4edda")
        self.converted_preview.configure_tag("expense", background="#f8d7da")

    def _create_action_section(self, parent):
        """Create action buttons."""
        frame = ttk.Frame(parent)
        frame.grid(row=3, column=0, sticky="ew")

        # Status label (updated to show current state)
        self.status_var = tk.StringVar(value="Выберите файл для начала")
        ttk.Label(frame, textvariable=self.status_var).pack(side="left")

        # === LEARNING: Button states ===
        # state="disabled" makes button unclickable and grayed out
        # Later: button.config(state="normal") to enable
        # [C++/Qt] Like: button->setEnabled(false)

        # Export button (initially disabled)
        self.export_btn = ttk.Button(
            frame, text="Экспорт в CSV", command=self._export, state="disabled"
        )
        self.export_btn.pack(side="right")

        # Copy income to clipboard button
        self.copy_income_btn = ttk.Button(
            frame,
            text="Копировать доходы",
            command=self._copy_income_to_clipboard,
            state="disabled"
        )
        self.copy_income_btn.pack(side="right", padx=5)

        # Copy expenses to clipboard button
        self.copy_expenses_btn = ttk.Button(
            frame,
            text="Копировать расходы",
            command=self._copy_expenses_to_clipboard,
            state="disabled"
        )
        self.copy_expenses_btn.pack(side="right", padx=5)

        # Convert button
        self.convert_btn = ttk.Button(
            frame, text="Конвертировать", command=self._convert, state="disabled"
        )
        self.convert_btn.pack(side="right", padx=5)

    def _select_file(self):
        """
        Open file selection dialog.

        === LEARNING: filedialog module ===
        Provides standard file selection dialogs.
        [C++/Qt] Like QFileDialog::getOpenFileName()
        """
        # filetypes is a list of (description, pattern) tuples
        filetypes = [
            ("Банковские выписки", "*.csv *.xlsx"),
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx"),
            ("All files", "*.*")
        ]

        # askopenfilename shows the dialog and returns selected path (or "")
        path = filedialog.askopenfilename(
            title="Выберите файл выписки",
            filetypes=filetypes
        )

        # Empty string = user cancelled
        if path:
            self.file_path_var.set(path)
            self._load_file(path)

    def _load_file(self, path: str):
        """Load and preview file."""
        try:
            # Read transactions using the reader component
            self.raw_transactions = self.reader.read(path)
            self._update_raw_preview()

            # Enable convert button now that we have data
            # .config() modifies widget options
            self.convert_btn.config(state="normal")

            self.status_var.set(
                f"Загружено {len(self.raw_transactions)} транзакций"
            )
        except Exception as e:
            # === LEARNING: messagebox module ===
            # Shows standard message dialogs
            # [C++/Qt] Like QMessageBox::critical()
            messagebox.showerror(
                "Ошибка загрузки",
                f"Не удалось загрузить файл:\n{e}"
            )
            self.status_var.set("Ошибка загрузки файла")

    def _update_raw_preview(self):
        """Update raw data preview."""
        self.raw_preview.clear()
        for tx in self.raw_transactions:
            # add_row takes a list of values matching column order
            self.raw_preview.add_row([
                tx.operation_date,
                tx.category,
                tx.description,
                tx.amount,
                tx.status
            ])

    def _convert(self):
        """
        Convert transactions.

        === LEARNING: Dialog workflow ===
        1. Create dialog
        2. wait_window() blocks until dialog closes
        3. Check dialog.saved to see if user confirmed

        [C++/Qt] Like: if (dialog->exec() == QDialog::Accepted)
        """
        # Update config with current owner from UI
        self.config.owner = self.owner_var.get()

        # First conversion pass - may return unknown mappings
        self.converted_transactions, unknowns = self.converter.convert(
            self.raw_transactions
        )

        # Handle unknown mappings if any
        if unknowns:
            dialog = MappingDialog(self.root, unknowns, self.config)

            # === LEARNING: wait_window() ===
            # Blocks until the specified window is destroyed.
            # This is how we make dialogs "modal" (blocking).
            # [C++/Qt] Like: dialog->exec() blocking call
            self.root.wait_window(dialog.dialog)

            if dialog.saved:
                # Re-convert after user resolved unknowns
                # Create new converter to pick up updated config
                self.converter = BankConverter(self.config)
                self.converted_transactions, _ = self.converter.convert(
                    self.raw_transactions
                )

        self._update_converted_preview()

        # Enable export buttons
        self.export_btn.config(state="normal")
        self.copy_income_btn.config(state="normal")
        self.copy_expenses_btn.config(state="normal")

        # Switch to converted tab
        self.notebook.select(1)  # 0 = first tab, 1 = second tab

        # === LEARNING: Generator expression with sum() ===
        # sum(1 for x in items if condition) counts items matching condition
        # [C++] Like: std::count_if(items.begin(), items.end(), predicate)
        income_count = sum(
            1 for tx in self.converted_transactions
            if tx.transaction_type.value == "income"
        )
        expense_count = len(self.converted_transactions) - income_count

        self.status_var.set(
            f"Конвертировано: {income_count} доходов, {expense_count} расходов"
        )

    def _update_converted_preview(self):
        """Update converted data preview."""
        self.converted_preview.clear()

        for tx in self.converted_transactions:
            # Determine display label and tag for row coloring
            type_label = "Доход" if tx.transaction_type.value == "income" else "Расход"
            tag = "income" if tx.transaction_type.value == "income" else "expense"

            # add_row with tags= for row styling
            self.converted_preview.add_row(
                [
                    tx.owner,
                    tx.date,
                    str(tx.amount),
                    tx.purpose,
                    tx.tag,
                    type_label
                ],
                tags=(tag,)  # Single-element tuple: (value,)
            )

    def _export(self):
        """Export to CSV file."""
        # asksaveasfilename shows "Save As" dialog
        path = filedialog.asksaveasfilename(
            title="Сохранить как",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile="budget_export.csv"
        )

        if path:
            try:
                self.writer.write(self.converted_transactions, path)
                messagebox.showinfo(
                    "Успешно",
                    f"Файл успешно сохранен:\n{path}"
                )
            except Exception as e:
                messagebox.showerror(
                    "Ошибка сохранения",
                    f"Не удалось сохранить файл:\n{e}"
                )

    def _copy_income_to_clipboard(self):
        """
        Copy INCOME transactions to clipboard.

        === LEARNING: Clipboard operations ===
        Tkinter provides clipboard access through the root window.
        Each copy button copies only its relevant section for direct pasting.
        """
        text = self.writer.to_clipboard_text_income(self.converted_transactions)

        # Clear existing clipboard content
        self.root.clipboard_clear()

        # Append new content (append because you could add multiple items)
        self.root.clipboard_append(text)

        self.status_var.set("Доходы скопированы в буфер обмена!")

    def _copy_expenses_to_clipboard(self):
        """
        Copy EXPENSE transactions to clipboard.

        === LEARNING: Parallel method for expenses ===
        Same clipboard logic but for expenses section.
        """
        text = self.writer.to_clipboard_text_expenses(self.converted_transactions)

        # Clear existing clipboard content
        self.root.clipboard_clear()

        # Append new content
        self.root.clipboard_append(text)

        self.status_var.set("Расходы скопированы в буфер обмена!")

    def _edit_config(self):
        """Open configuration editor dialog."""
        dialog = ConfigDialog(self.root, self.config)
        self.root.wait_window(dialog.dialog)

        if dialog.saved:
            # Reload config to pick up changes
            self.config = ConfigManager()
            self.converter = BankConverter(self.config)
            self.owner_var.set(self.config.owner)
            self.status_var.set("Настройки сохранены")

    def _open_config_folder(self):
        """
        Open folder containing config file.

        === LEARNING: Platform-specific code ===
        os.name returns:
        - 'nt' on Windows
        - 'posix' on Linux/Mac

        [C++] Like: #ifdef _WIN32 ... #else ... #endif
        """
        # === LEARNING: Lazy imports ===
        # Import inside function when:
        # 1. Module is rarely needed
        # 2. Import has side effects
        # 3. Avoiding circular imports
        import os
        import subprocess
        from pathlib import Path

        config_path = Path(self.config.config_path)

        # Save config first to ensure file exists
        self.config.save()

        # === LEARNING: Platform detection ===
        # [C++] Like: #ifdef _WIN32
        if os.name == 'nt':  # Windows
            # /select, highlights the file in Explorer
            subprocess.run(['explorer', '/select,', str(config_path)])
        else:  # macOS/Linux (posix)
            folder = config_path.parent
            if os.name == 'posix':
                # os.uname().sysname returns 'Darwin' on macOS
                opener = 'open' if os.uname().sysname == 'Darwin' else 'xdg-open'
                subprocess.run([opener, str(folder)])

    def run(self):
        """
        Start the application.

        === LEARNING: mainloop() ===
        mainloop() starts the tkinter event loop.
        It processes events (clicks, keypresses, etc.) until the window closes.

        [C++/Qt] Like: return app.exec();

        This call BLOCKS - nothing after mainloop() runs until the window closes.
        """
        # === LEARNING: Loading file on startup ===
        # If a file was passed (via command line or drag-drop onto .py file),
        # load it after the UI is ready but before entering the event loop.
        # We use after() to schedule loading after the window is displayed.
        if self._initial_file:
            # after(ms, func) schedules func to run after ms milliseconds
            # Using 100ms delay ensures window is fully rendered first
            self.root.after(100, lambda: self._load_initial_file())

        self.root.mainloop()

    def _load_initial_file(self):
        """
        Load the initial file specified at startup.

        === LEARNING: Deferred loading with after() ===
        This is called via after() to ensure the window is fully displayed
        before we start loading and processing the file.
        """
        import os
        if self._initial_file and os.path.exists(self._initial_file):
            self.file_path_var.set(self._initial_file)
            self._load_file(self._initial_file)
