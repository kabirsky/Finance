"""
Preview frame component for displaying data in a table.

=== LEARNING: This module demonstrates ===
- Class inheritance with super().__init__()
- Tkinter widget composition
- Grid geometry manager
- The **kwargs pattern for flexible arguments
"""

# =============================================================================
# IMPORTS
# =============================================================================
# === LEARNING: Import Aliases ===
# 'as tk' creates a shorter alias for the module
# [C++] Like: namespace tk = tkinter;
import tkinter as tk

# === LEARNING: Submodule imports ===
# ttk is a submodule containing "themed" (modern-looking) widgets
from tkinter import ttk

from typing import List


class PreviewFrame(ttk.Frame):
    """
    Scrollable treeview for data preview.

    === LEARNING: Inheritance ===
    PreviewFrame inherits from ttk.Frame (a container widget).

    [C++] Like:
          class PreviewFrame : public ttk::Frame {
          public:
              PreviewFrame(Widget* parent, const std::vector<std::string>& columns);
          };

    In Python, inheritance is declared in parentheses after class name.
    Multiple inheritance is allowed: class Foo(Bar, Baz):
    """

    def __init__(self, parent, columns: List[str]):
        """
        Initialize preview frame.

        === LEARNING: Calling Parent Constructor ===
        super().__init__(parent) calls the parent class's __init__.

        [C++] Like calling base class constructor in initializer list:
              PreviewFrame(Widget* parent, ...)
                  : ttk::Frame(parent)
              { }

        In Python 2, you had to write: super(PreviewFrame, self).__init__()
        Python 3 simplified this to just: super().__init__()

        Args:
            parent: Parent widget.
            columns: List of column names.
        """
        # Call parent constructor with parent widget
        super().__init__(parent)

        # Store columns as instance variable for later use
        self.columns = columns

        # Setup the UI (common pattern to separate __init__ from UI setup)
        self._setup_ui()

    def _setup_ui(self):
        """
        Create treeview with scrollbars.

        === LEARNING: Tkinter Grid Geometry Manager ===
        Tkinter has 3 geometry managers for laying out widgets:
        1. pack() - simple stacking (vertical/horizontal)
        2. grid() - table-based layout (rows and columns)
        3. place() - absolute positioning (rarely used)

        [C++/Qt] Grid is similar to QGridLayout:
                 - grid(row=0, column=0) = layout->addWidget(widget, 0, 0);
                 - sticky="nsew" = widget fills its cell (N/S/E/W = top/bottom/right/left)
                 - weight=1 means the row/column expands with window resize
        """
        # Configure this frame's grid behavior
        # weight=1 means column/row 0 will expand to fill available space
        # [C++/Qt] Like: setColumnStretch(0, 1); setRowStretch(0, 1);
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # === LEARNING: ttk.Treeview ===
        # Treeview is tkinter's table/tree widget - displays tabular data
        # [C++/Qt] Similar to QTableView or QTreeView
        #
        # Parameters:
        # - self: parent widget (this frame)
        # - columns: list of column identifiers
        # - show="headings": show only column headers (no tree icons)
        # - selectmode="browse": single selection only
        self.tree = ttk.Treeview(
            self,
            columns=self.columns,
            show="headings",
            selectmode="browse"
        )

        # Place treeview in grid at row 0, column 0
        # sticky="nsew" = expand in all directions (North/South/East/West)
        self.tree.grid(row=0, column=0, sticky="nsew")

        # === LEARNING: Configuring columns ===
        # [C++/Qt] Like setting up QHeaderView columns
        for col in self.columns:
            # heading() sets the column header text
            # anchor="w" = text aligned west (left)
            self.tree.heading(col, text=col, anchor="w")

            # Set column widths based on content type
            # === LEARNING: 'in' with tuple for multiple checks ===
            # [C++] Like: if (col == "Дата" || col == "Статус" || ...)
            if col in ("Дата", "Статус", "Тип", "Тег"):
                width = 80
            elif col in ("Сумма",):
                # Note: (item,) is a single-element tuple, (item) is just parentheses
                width = 100
            elif col in ("Описание", "Назначение", "Категория"):
                width = 150
            else:
                width = 100

            # column() configures column display properties
            self.tree.column(col, width=width, minwidth=50)

        # === LEARNING: Scrollbars ===
        # Scrollbars are separate widgets that connect to scrollable widgets
        # [C++/Qt] Similar to QScrollArea, but explicit connection
        #
        # Two-way binding:
        # 1. scrollbar.command = tree.yview (scrollbar controls tree)
        # 2. tree.yscrollcommand = scrollbar.set (tree updates scrollbar)

        # Vertical scrollbar
        v_scroll = ttk.Scrollbar(
            self, orient="vertical", command=self.tree.yview
        )
        v_scroll.grid(row=0, column=1, sticky="ns")  # ns = stretch vertically
        self.tree.configure(yscrollcommand=v_scroll.set)

        # Horizontal scrollbar
        h_scroll = ttk.Scrollbar(
            self, orient="horizontal", command=self.tree.xview
        )
        h_scroll.grid(row=1, column=0, sticky="ew")  # ew = stretch horizontally
        self.tree.configure(xscrollcommand=h_scroll.set)

    def clear(self):
        """
        Remove all rows.

        === LEARNING: Treeview item management ===
        get_children() returns tuple of item IDs in the treeview
        delete() removes items by ID
        """
        # Iterate over all items and delete each
        for item in self.tree.get_children():
            self.tree.delete(item)

    def add_row(self, values: List[str], tags: tuple = ()):
        """
        Add a row to the treeview.

        === LEARNING: Default mutable argument gotcha ===
        Note: tags: tuple = () is safe because tuples are IMMUTABLE.
        DON'T DO: tags: list = [] - this is a common Python bug!

        [C++] Default args work similarly, but Python has the "mutable
              default argument" trap where mutable defaults (lists, dicts)
              are shared between calls.

        Args:
            values: List of values for each column.
            tags: Optional tags for row styling.
        """
        # insert("", "end", ...) adds at root level, at the end
        # "" = parent (empty = root level)
        # "end" = position (at the end)
        self.tree.insert("", "end", values=values, tags=tags)

    def get_row_count(self) -> int:
        """Get number of rows in the treeview."""
        # len() works on any sequence - list, tuple, string, etc.
        # [C++] Like: container.size()
        return len(self.tree.get_children())

    def configure_tag(self, tag_name: str, **options):
        """
        Configure a tag for row styling.

        === LEARNING: **kwargs (keyword arguments) ===
        **options collects all extra keyword arguments into a dict.

        [C++] No direct equivalent. You'd need:
              - A struct/class with optional fields
              - A map<string, variant> for dynamic options
              - Multiple overloaded methods

        Example calls:
            configure_tag("income", background="green")
            configure_tag("expense", background="red", foreground="white")

        The **options dict would be:
            {"background": "green"} or {"background": "red", "foreground": "white"}

        Args:
            tag_name: Name of the tag.
            **options: Tag options (background, foreground, etc.).
        """
        # === LEARNING: Unpacking kwargs ===
        # **options passes the dict as keyword arguments to tag_configure
        # [C++] Like using std::apply to unpack arguments (C++17)
        #
        # Equivalent to: self.tree.tag_configure(tag_name, background="...", foreground="...")
        self.tree.tag_configure(tag_name, **options)
