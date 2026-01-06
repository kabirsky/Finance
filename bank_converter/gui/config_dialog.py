"""Configuration editor dialog."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from ..config.manager import ConfigManager


class ConfigDialog:
    """Dialog for editing application configuration."""

    def __init__(self, parent: tk.Tk, config: ConfigManager):
        """Initialize config dialog.

        Args:
            parent: Parent window.
            config: ConfigManager instance.
        """
        self.config = config
        self.saved = False

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Настройки")
        self.dialog.geometry("800x600")
        self.dialog.minsize(600, 400)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 800) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 600) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self._setup_ui()
        self._load_config()

        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)

    def _setup_ui(self):
        """Create dialog UI."""
        # Main container
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill="both", expand=True)

        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))

        # Create tabs
        self._create_general_tab()
        self._create_categories_tab()
        self._create_vendors_tab()
        self._create_skip_tab()

        # Buttons frame
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x")

        ttk.Button(btn_frame, text="Сохранить", command=self._save).pack(side="right", padx=(5, 0))
        ttk.Button(btn_frame, text="Отмена", command=self._on_close).pack(side="right")

    def _create_general_tab(self):
        """Create general settings tab."""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Общие")

        # Owner
        owner_frame = ttk.LabelFrame(frame, text="Владелец по умолчанию", padding="10")
        owner_frame.pack(fill="x", pady=(0, 10))

        self.owner_var = tk.StringVar()
        ttk.Entry(owner_frame, textvariable=self.owner_var, width=30).pack(anchor="w")

        # Output tags
        tags_frame = ttk.LabelFrame(frame, text="Доступные теги (через запятую)", padding="10")
        tags_frame.pack(fill="x")

        self.tags_var = tk.StringVar()
        ttk.Entry(tags_frame, textvariable=self.tags_var, width=60).pack(anchor="w", fill="x")

    def _create_categories_tab(self):
        """Create category mappings tab."""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Категории")

        # Instructions
        ttk.Label(
            frame,
            text="Соответствие банковских категорий → тегам бюджета",
            font=("TkDefaultFont", 9, "italic")
        ).pack(anchor="w", pady=(0, 5))

        # List frame
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill="both", expand=True)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Treeview
        columns = ("category", "tag")
        self.cat_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        self.cat_tree.heading("category", text="Категория банка")
        self.cat_tree.heading("tag", text="Тег бюджета")
        self.cat_tree.column("category", width=250)
        self.cat_tree.column("tag", width=150)
        self.cat_tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.cat_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.cat_tree.configure(yscrollcommand=scrollbar.set)

        # Edit frame
        edit_frame = ttk.Frame(frame)
        edit_frame.pack(fill="x", pady=(10, 0))

        ttk.Label(edit_frame, text="Категория:").pack(side="left")
        self.cat_category_var = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=self.cat_category_var, width=25).pack(side="left", padx=(5, 10))

        ttk.Label(edit_frame, text="Тег:").pack(side="left")
        self.cat_tag_var = tk.StringVar()
        self.cat_tag_combo = ttk.Combobox(edit_frame, textvariable=self.cat_tag_var, width=15)
        self.cat_tag_combo.pack(side="left", padx=(5, 10))

        ttk.Button(edit_frame, text="Добавить/Изменить", command=self._add_category).pack(side="left", padx=(0, 5))
        ttk.Button(edit_frame, text="Удалить", command=self._delete_category).pack(side="left")

        # Bind selection
        self.cat_tree.bind("<<TreeviewSelect>>", self._on_category_select)

    def _create_vendors_tab(self):
        """Create vendor overrides tab."""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Продавцы")

        # Instructions
        ttk.Label(
            frame,
            text="Переопределение для конкретных продавцов (приоритет выше категорий)",
            font=("TkDefaultFont", 9, "italic")
        ).pack(anchor="w", pady=(0, 5))

        # List frame
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill="both", expand=True)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Treeview
        columns = ("vendor", "tag", "name")
        self.vendor_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        self.vendor_tree.heading("vendor", text="Продавец (из банка)")
        self.vendor_tree.heading("tag", text="Тег")
        self.vendor_tree.heading("name", text="Название")
        self.vendor_tree.column("vendor", width=200)
        self.vendor_tree.column("tag", width=120)
        self.vendor_tree.column("name", width=150)
        self.vendor_tree.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.vendor_tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.vendor_tree.configure(yscrollcommand=scrollbar.set)

        # Edit frame
        edit_frame = ttk.Frame(frame)
        edit_frame.pack(fill="x", pady=(10, 0))

        ttk.Label(edit_frame, text="Продавец:").pack(side="left")
        self.vendor_name_var = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=self.vendor_name_var, width=20).pack(side="left", padx=(5, 10))

        ttk.Label(edit_frame, text="Тег:").pack(side="left")
        self.vendor_tag_var = tk.StringVar()
        self.vendor_tag_combo = ttk.Combobox(edit_frame, textvariable=self.vendor_tag_var, width=12)
        self.vendor_tag_combo.pack(side="left", padx=(5, 10))

        ttk.Label(edit_frame, text="Название:").pack(side="left")
        self.vendor_purpose_var = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=self.vendor_purpose_var, width=15).pack(side="left", padx=(5, 10))

        ttk.Button(edit_frame, text="Добавить/Изменить", command=self._add_vendor).pack(side="left", padx=(0, 5))
        ttk.Button(edit_frame, text="Удалить", command=self._delete_vendor).pack(side="left")

        # Bind selection
        self.vendor_tree.bind("<<TreeviewSelect>>", self._on_vendor_select)

    def _create_skip_tab(self):
        """Create skip descriptions tab."""
        frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(frame, text="Пропуск")

        # Instructions
        ttk.Label(
            frame,
            text="Транзакции с этими описаниями будут пропущены (например, внутренние переводы)",
            font=("TkDefaultFont", 9, "italic")
        ).pack(anchor="w", pady=(0, 5))

        # List frame
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill="both", expand=True)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # Listbox
        self.skip_listbox = tk.Listbox(list_frame, height=12)
        self.skip_listbox.grid(row=0, column=0, sticky="nsew")

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.skip_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.skip_listbox.configure(yscrollcommand=scrollbar.set)

        # Edit frame
        edit_frame = ttk.Frame(frame)
        edit_frame.pack(fill="x", pady=(10, 0))

        ttk.Label(edit_frame, text="Описание:").pack(side="left")
        self.skip_var = tk.StringVar()
        ttk.Entry(edit_frame, textvariable=self.skip_var, width=40).pack(side="left", padx=(5, 10))

        ttk.Button(edit_frame, text="Добавить", command=self._add_skip).pack(side="left", padx=(0, 5))
        ttk.Button(edit_frame, text="Удалить", command=self._delete_skip).pack(side="left")

        # Bind selection
        self.skip_listbox.bind("<<ListboxSelect>>", self._on_skip_select)

    def _load_config(self):
        """Load current config into UI."""
        # General
        self.owner_var.set(self.config.owner)
        self.tags_var.set(", ".join(self.config.output_tags))

        # Update tag combos
        tags = self.config.output_tags
        self.cat_tag_combo["values"] = tags
        self.vendor_tag_combo["values"] = tags

        # Categories
        for category, tag in sorted(self.config.category_mappings.items()):
            self.cat_tree.insert("", "end", values=(category, tag))

        # Vendors
        for vendor, data in sorted(self.config.vendor_overrides.items()):
            tag = data.get("tag", "")
            name = data.get("назначение", "")
            self.vendor_tree.insert("", "end", values=(vendor, tag, name))

        # Skip descriptions
        for desc in self.config.skip_descriptions:
            self.skip_listbox.insert("end", desc)

    def _on_category_select(self, event):
        """Handle category selection."""
        selection = self.cat_tree.selection()
        if selection:
            item = self.cat_tree.item(selection[0])
            values = item["values"]
            self.cat_category_var.set(values[0])
            self.cat_tag_var.set(values[1])

    def _on_vendor_select(self, event):
        """Handle vendor selection."""
        selection = self.vendor_tree.selection()
        if selection:
            item = self.vendor_tree.item(selection[0])
            values = item["values"]
            self.vendor_name_var.set(values[0])
            self.vendor_tag_var.set(values[1])
            self.vendor_purpose_var.set(values[2])

    def _on_skip_select(self, event):
        """Handle skip description selection."""
        selection = self.skip_listbox.curselection()
        if selection:
            self.skip_var.set(self.skip_listbox.get(selection[0]))

    def _add_category(self):
        """Add or update category mapping."""
        category = self.cat_category_var.get().strip()
        tag = self.cat_tag_var.get().strip()

        if not category or not tag:
            messagebox.showwarning("Предупреждение", "Заполните категорию и тег")
            return

        # Check if exists and update
        for item in self.cat_tree.get_children():
            values = self.cat_tree.item(item)["values"]
            if values[0] == category:
                self.cat_tree.item(item, values=(category, tag))
                return

        # Add new
        self.cat_tree.insert("", "end", values=(category, tag))
        self.cat_category_var.set("")
        self.cat_tag_var.set("")

    def _delete_category(self):
        """Delete selected category mapping."""
        selection = self.cat_tree.selection()
        if selection:
            self.cat_tree.delete(selection[0])
            self.cat_category_var.set("")
            self.cat_tag_var.set("")

    def _add_vendor(self):
        """Add or update vendor override."""
        vendor = self.vendor_name_var.get().strip()
        tag = self.vendor_tag_var.get().strip()
        purpose = self.vendor_purpose_var.get().strip()

        if not vendor or not tag:
            messagebox.showwarning("Предупреждение", "Заполните продавца и тег")
            return

        if not purpose:
            purpose = vendor

        # Check if exists and update
        for item in self.vendor_tree.get_children():
            values = self.vendor_tree.item(item)["values"]
            if values[0] == vendor:
                self.vendor_tree.item(item, values=(vendor, tag, purpose))
                return

        # Add new
        self.vendor_tree.insert("", "end", values=(vendor, tag, purpose))
        self.vendor_name_var.set("")
        self.vendor_tag_var.set("")
        self.vendor_purpose_var.set("")

    def _delete_vendor(self):
        """Delete selected vendor override."""
        selection = self.vendor_tree.selection()
        if selection:
            self.vendor_tree.delete(selection[0])
            self.vendor_name_var.set("")
            self.vendor_tag_var.set("")
            self.vendor_purpose_var.set("")

    def _add_skip(self):
        """Add skip description."""
        desc = self.skip_var.get().strip()
        if not desc:
            return

        # Check if already exists
        items = self.skip_listbox.get(0, "end")
        if desc not in items:
            self.skip_listbox.insert("end", desc)
            self.skip_var.set("")

    def _delete_skip(self):
        """Delete selected skip description."""
        selection = self.skip_listbox.curselection()
        if selection:
            self.skip_listbox.delete(selection[0])
            self.skip_var.set("")

    def _save(self):
        """Save configuration."""
        # Update owner
        self.config._data["owner"] = self.owner_var.get().strip()

        # Update tags
        tags_str = self.tags_var.get()
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]
        self.config._data["output_tags"] = tags

        # Update category mappings
        category_mappings = {}
        for item in self.cat_tree.get_children():
            values = self.cat_tree.item(item)["values"]
            category_mappings[values[0]] = values[1]
        self.config._data["category_mappings"] = category_mappings

        # Update vendor overrides
        vendor_overrides = {}
        for item in self.vendor_tree.get_children():
            values = self.vendor_tree.item(item)["values"]
            vendor_overrides[values[0]] = {
                "tag": values[1],
                "назначение": values[2]
            }
        self.config._data["vendor_overrides"] = vendor_overrides

        # Update skip descriptions
        skip_descriptions = list(self.skip_listbox.get(0, "end"))
        self.config._data["skip_descriptions"] = skip_descriptions

        # Save to file
        self.config.save()
        self.saved = True
        messagebox.showinfo("Сохранено", "Настройки сохранены")
        self.dialog.destroy()

    def _on_close(self):
        """Handle dialog close."""
        self.dialog.destroy()
