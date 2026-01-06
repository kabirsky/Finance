"""Main application window."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Optional

from ..core.reader import BankFileReader
from ..core.converter import BankConverter
from ..core.writer import BudgetWriter
from ..core.models import BankTransaction, BudgetTransaction, UnknownMapping
from ..config.manager import ConfigManager
from .preview_frame import PreviewFrame
from .mapping_dialog import MappingDialog
from .config_dialog import ConfigDialog


class BankConverterApp:
    """Main application window."""

    def __init__(self):
        """Initialize the application."""
        self.root = tk.Tk()
        self.root.title("Bank to Budget Converter")
        self.root.geometry("1000x700")
        self.root.minsize(800, 500)

        # Initialize components
        self.config = ConfigManager()
        self.reader = BankFileReader()
        self.converter = BankConverter(self.config)
        self.writer = BudgetWriter()

        # Data storage
        self.raw_transactions: List[BankTransaction] = []
        self.converted_transactions: List[BudgetTransaction] = []

        self._setup_styles()
        self._setup_ui()

    def _setup_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.configure("Title.TLabel", font=("TkDefaultFont", 12, "bold"))

    def _setup_ui(self):
        """Create main UI layout."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)  # Preview frame expands

        # Top section: File selection
        self._create_file_section(main_frame)

        # Settings section
        self._create_settings_section(main_frame)

        # Main section: Preview tabs
        self._create_preview_section(main_frame)

        # Bottom section: Action buttons
        self._create_action_section(main_frame)

    def _create_file_section(self, parent):
        """Create file selection area."""
        frame = ttk.LabelFrame(parent, text="Входной файл", padding="10")
        frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Файл:").grid(row=0, column=0, padx=(0, 10))

        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(
            frame, textvariable=self.file_path_var, state="readonly"
        )
        self.file_entry.grid(row=0, column=1, sticky="ew", padx=(0, 10))

        ttk.Button(
            frame, text="Выбрать...", command=self._select_file
        ).grid(row=0, column=2)

    def _create_settings_section(self, parent):
        """Create settings bar."""
        frame = ttk.LabelFrame(parent, text="Настройки", padding="10")
        frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # Owner name
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

        # Config file path info
        ttk.Button(
            frame,
            text="Открыть папку конфига",
            command=self._open_config_folder
        ).pack(side="left")

    def _create_preview_section(self, parent):
        """Create tabbed preview area."""
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=2, column=0, sticky="nsew", pady=(0, 10))

        # Raw data preview
        self.raw_preview = PreviewFrame(self.notebook, columns=[
            "Дата", "Категория", "Описание", "Сумма", "Статус"
        ])
        self.notebook.add(self.raw_preview, text="Исходные данные")

        # Converted preview
        self.converted_preview = PreviewFrame(self.notebook, columns=[
            "Чей", "Дата", "Сумма", "Назначение", "Тег", "Тип"
        ])
        self.notebook.add(self.converted_preview, text="Результат")

        # Configure row colors for converted preview
        self.converted_preview.configure_tag("income", background="#d4edda")
        self.converted_preview.configure_tag("expense", background="#f8d7da")

    def _create_action_section(self, parent):
        """Create action buttons."""
        frame = ttk.Frame(parent)
        frame.grid(row=3, column=0, sticky="ew")

        # Status label
        self.status_var = tk.StringVar(value="Выберите файл для начала")
        ttk.Label(frame, textvariable=self.status_var).pack(side="left")

        # Export button
        self.export_btn = ttk.Button(
            frame, text="Экспорт в CSV", command=self._export, state="disabled"
        )
        self.export_btn.pack(side="right")

        # Copy to clipboard button
        self.copy_btn = ttk.Button(
            frame,
            text="Копировать в буфер",
            command=self._copy_to_clipboard,
            state="disabled"
        )
        self.copy_btn.pack(side="right", padx=5)

        # Convert button
        self.convert_btn = ttk.Button(
            frame, text="Конвертировать", command=self._convert, state="disabled"
        )
        self.convert_btn.pack(side="right", padx=5)

    def _select_file(self):
        """Open file selection dialog."""
        filetypes = [
            ("Банковские выписки", "*.csv *.xlsx"),
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx"),
            ("All files", "*.*")
        ]
        path = filedialog.askopenfilename(
            title="Выберите файл выписки",
            filetypes=filetypes
        )
        if path:
            self.file_path_var.set(path)
            self._load_file(path)

    def _load_file(self, path: str):
        """Load and preview file."""
        try:
            self.raw_transactions = self.reader.read(path)
            self._update_raw_preview()
            self.convert_btn.config(state="normal")
            self.status_var.set(
                f"Загружено {len(self.raw_transactions)} транзакций"
            )
        except Exception as e:
            messagebox.showerror(
                "Ошибка загрузки",
                f"Не удалось загрузить файл:\n{e}"
            )
            self.status_var.set("Ошибка загрузки файла")

    def _update_raw_preview(self):
        """Update raw data preview."""
        self.raw_preview.clear()
        for tx in self.raw_transactions:
            self.raw_preview.add_row([
                tx.operation_date,
                tx.category,
                tx.description,
                tx.amount,
                tx.status
            ])

    def _convert(self):
        """Convert transactions."""
        # Update owner from UI
        self.config.owner = self.owner_var.get()

        # First conversion pass
        self.converted_transactions, unknowns = self.converter.convert(
            self.raw_transactions
        )

        # Handle unknown mappings if any
        if unknowns:
            dialog = MappingDialog(self.root, unknowns, self.config)
            self.root.wait_window(dialog.dialog)

            if dialog.saved:
                # Re-convert after user resolved unknowns
                self.converter = BankConverter(self.config)  # Reload config
                self.converted_transactions, _ = self.converter.convert(
                    self.raw_transactions
                )

        self._update_converted_preview()
        self.export_btn.config(state="normal")
        self.copy_btn.config(state="normal")
        self.notebook.select(1)  # Switch to converted tab

        # Count income vs expenses
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
            type_label = "Доход" if tx.transaction_type.value == "income" else "Расход"
            tag = "income" if tx.transaction_type.value == "income" else "expense"

            self.converted_preview.add_row(
                [
                    tx.owner,
                    tx.date,
                    str(tx.amount),
                    tx.purpose,
                    tx.tag,
                    type_label
                ],
                tags=(tag,)
            )

    def _export(self):
        """Export to CSV file."""
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

    def _copy_to_clipboard(self):
        """Copy converted data to clipboard."""
        text = self.writer.to_clipboard_text(self.converted_transactions)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.status_var.set("Данные скопированы в буфер обмена!")

    def _edit_config(self):
        """Open configuration editor dialog."""
        dialog = ConfigDialog(self.root, self.config)
        self.root.wait_window(dialog.dialog)

        if dialog.saved:
            # Reload config and update UI
            self.config = ConfigManager()
            self.converter = BankConverter(self.config)
            self.owner_var.set(self.config.owner)
            self.status_var.set("Настройки сохранены")

    def _open_config_folder(self):
        """Open folder containing config file."""
        import os
        import subprocess
        from pathlib import Path

        config_path = Path(self.config.config_path)

        # Save config first to ensure file exists
        self.config.save()

        if os.name == 'nt':  # Windows
            subprocess.run(['explorer', '/select,', str(config_path)])
        else:  # macOS/Linux
            folder = config_path.parent
            if os.name == 'posix':
                subprocess.run(['open' if os.uname().sysname == 'Darwin' else 'xdg-open', str(folder)])

    def run(self):
        """Start the application."""
        self.root.mainloop()
