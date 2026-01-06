"""Preview frame component for displaying data in a table."""

import tkinter as tk
from tkinter import ttk
from typing import List


class PreviewFrame(ttk.Frame):
    """Scrollable treeview for data preview."""

    def __init__(self, parent, columns: List[str]):
        """Initialize preview frame.

        Args:
            parent: Parent widget.
            columns: List of column names.
        """
        super().__init__(parent)
        self.columns = columns
        self._setup_ui()

    def _setup_ui(self):
        """Create treeview with scrollbars."""
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Treeview
        self.tree = ttk.Treeview(
            self,
            columns=self.columns,
            show="headings",
            selectmode="browse"
        )
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Configure columns
        for col in self.columns:
            self.tree.heading(col, text=col, anchor="w")
            # Set reasonable default widths
            if col in ("Дата", "Статус", "Тип", "Тег"):
                width = 80
            elif col in ("Сумма",):
                width = 100
            elif col in ("Описание", "Назначение", "Категория"):
                width = 150
            else:
                width = 100
            self.tree.column(col, width=width, minwidth=50)

        # Vertical scrollbar
        v_scroll = ttk.Scrollbar(
            self, orient="vertical", command=self.tree.yview
        )
        v_scroll.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=v_scroll.set)

        # Horizontal scrollbar
        h_scroll = ttk.Scrollbar(
            self, orient="horizontal", command=self.tree.xview
        )
        h_scroll.grid(row=1, column=0, sticky="ew")
        self.tree.configure(xscrollcommand=h_scroll.set)

    def clear(self):
        """Remove all rows."""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def add_row(self, values: List[str], tags: tuple = ()):
        """Add a row to the treeview.

        Args:
            values: List of values for each column.
            tags: Optional tags for row styling.
        """
        self.tree.insert("", "end", values=values, tags=tags)

    def get_row_count(self) -> int:
        """Get number of rows in the treeview."""
        return len(self.tree.get_children())

    def configure_tag(self, tag_name: str, **options):
        """Configure a tag for row styling.

        Args:
            tag_name: Name of the tag.
            **options: Tag options (background, foreground, etc.).
        """
        self.tree.tag_configure(tag_name, **options)
