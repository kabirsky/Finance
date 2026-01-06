"""
Dialog for resolving unknown category/vendor mappings.

=== LEARNING: This module demonstrates ===
- Modal dialog pattern with Toplevel
- Event binding with lambda functions
- Nested functions (closures)
- StringVar for two-way data binding
- Scrollable frame pattern (Canvas + Frame)
"""

# =============================================================================
# IMPORTS
# =============================================================================
import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any

from ..core.models import UnknownMapping
from ..config.manager import ConfigManager


class MappingDialog:
    """
    Dialog for resolving unknown category/vendor mappings.

    === LEARNING: Dialog Pattern ===
    This is NOT a subclass of Toplevel (the tkinter dialog window).
    Instead, it CONTAINS a Toplevel as self.dialog.

    This is composition vs inheritance. Composition is often preferred
    because it's more flexible.

    [C++/Qt] Like having a QDialog* member rather than inheriting QDialog:
             class MappingDialog {
                 QDialog* dialog;
             };

    The dialog is "modal" - it blocks interaction with the parent window
    until closed. This is done with grab_set().
    """

    def __init__(
        self,
        parent: tk.Tk,
        unknowns: List[UnknownMapping],
        config: ConfigManager
    ):
        """
        Initialize mapping dialog.

        === LEARNING: Multi-line function signature ===
        When a function has many parameters, Python allows splitting
        across lines. The closing paren can be on its own line.

        Args:
            parent: Parent window.
            unknowns: List of unknown mappings to resolve.
            config: ConfigManager for saving mappings.
        """
        self.config = config
        self.unknowns = unknowns

        # === LEARNING: Complex type hint ===
        # Dict[int, Dict[str, Any]] = dictionary with int keys and dict values
        # [C++] Like: std::map<int, std::map<std::string, std::any>>
        self.entries: Dict[int, Dict[str, Any]] = {}

        # Track whether user saved or skipped
        self.saved = False

        # === LEARNING: tk.Toplevel ===
        # Toplevel creates a new window (separate from root window).
        # [C++/Qt] Like: new QDialog(parent)
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Неизвестные категории/продавцы")
        self.dialog.geometry("700x500")  # Width x Height

        # === LEARNING: transient() ===
        # Makes this dialog "belong" to the parent window.
        # - Appears above parent
        # - Minimizes/restores with parent
        # - May not appear in taskbar (OS dependent)
        # [C++/Qt] Like: setWindowFlags(Qt::Dialog)
        self.dialog.transient(parent)

        # === LEARNING: grab_set() ===
        # Makes this dialog MODAL - user can't interact with parent
        # until this dialog is closed.
        # [C++/Qt] Like: dialog->setModal(true) or dialog->exec()
        self.dialog.grab_set()

        # Center the dialog over parent window
        # update_idletasks() processes pending geometry changes
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 700) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 500) // 2
        # geometry("+X+Y") sets position without changing size
        self.dialog.geometry(f"+{x}+{y}")

        self._setup_ui()

        # === LEARNING: Window close protocol ===
        # Handle the X button (window close) event
        # [C++/Qt] Like: connect(closeButton, &QPushButton::clicked, ...)
        self.dialog.protocol("WM_DELETE_WINDOW", self._skip)

    def _setup_ui(self):
        """Create dialog UI."""
        # Main container frame with padding
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill="both", expand=True)

        # Instructions label
        # wraplength = max width before text wraps to next line
        instructions = ttk.Label(
            main_frame,
            text="Назначьте теги для неизвестных категорий и продавцов.\n"
                 "Эти настройки будут сохранены для будущего использования.",
            wraplength=650,
            justify="left"
        )
        instructions.pack(anchor="w", pady=(0, 10))

        # === LEARNING: Scrollable Frame Pattern ===
        # Tkinter doesn't have a scrollable frame widget, so we build one:
        # 1. Container Frame (holds Canvas + Scrollbar)
        # 2. Canvas (scrollable surface)
        # 3. Frame inside Canvas (holds actual content)
        #
        # [C++/Qt] Qt has QScrollArea which does this automatically

        container = ttk.Frame(main_frame)
        container.pack(fill="both", expand=True)

        # Canvas is the scrollable surface
        # highlightthickness=0 removes the focus border
        canvas = tk.Canvas(container, highlightthickness=0)

        scrollbar = ttk.Scrollbar(
            container, orient="vertical", command=canvas.yview
        )

        # This frame goes INSIDE the canvas and holds our content
        self.scroll_frame = ttk.Frame(canvas)

        # === LEARNING: Event binding with bind() ===
        # bind("<EventType>", handler) connects events to functions
        #
        # <Configure> fires when widget is resized
        # lambda e: ... creates an inline event handler
        #
        # [C++/Qt] Like: connect(widget, SIGNAL(resizeEvent()), ...)
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Create the frame as a window inside the canvas
        canvas_frame = canvas.create_window(
            (0, 0), window=self.scroll_frame, anchor="nw"
        )

        # === LEARNING: Nested function (closure) ===
        # Functions can be defined inside other functions.
        # They can access variables from the enclosing scope (closure).
        #
        # [C++] Like a lambda capturing by reference:
        #       auto configure_frame = [&canvas, canvas_frame](Event* e) { ... };
        def configure_frame(event):
            # This nested function can access canvas and canvas_frame
            # from the enclosing scope
            canvas.itemconfig(canvas_frame, width=event.width)

        canvas.bind("<Configure>", configure_frame)
        canvas.configure(yscrollcommand=scrollbar.set)

        # === LEARNING: Mouse wheel scrolling ===
        # bind_all() binds to ALL widgets in the application
        # event.delta is the scroll amount (120 units per "notch" on Windows)
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # === LEARNING: enumerate() for index + value ===
        # Creates pairs of (index, item) for iteration
        # [C++] Like using a loop counter:
        #       for (size_t i = 0; i < unknowns.size(); i++)
        for i, unknown in enumerate(self.unknowns):
            self._create_mapping_row(i, unknown)

        # Buttons at bottom
        btn_frame = ttk.Frame(self.dialog, padding="10")
        btn_frame.pack(fill="x")

        # === LEARNING: command= for button callbacks ===
        # command= takes a function reference (no parentheses!)
        # [C++/Qt] Like: connect(button, &QPushButton::clicked, this, &Dialog::save)
        ttk.Button(
            btn_frame, text="Сохранить и продолжить", command=self._save
        ).pack(side="right", padx=(5, 0))

        ttk.Button(
            btn_frame, text="Пропустить", command=self._skip
        ).pack(side="right")

    def _create_mapping_row(self, index: int, unknown: UnknownMapping):
        """
        Create a row for one unknown mapping.

        Each row has:
        - Type label (Category/Vendor)
        - Original value
        - Tag dropdown
        - Purpose entry (vendors only)

        Args:
            index: Index of the unknown mapping.
            unknown: UnknownMapping object.
        """
        frame = ttk.Frame(self.scroll_frame)
        frame.pack(fill="x", pady=5, padx=5)

        # === LEARNING: Ternary expression ===
        # value_if_true if condition else value_if_false
        # [C++] Like: condition ? value_if_true : value_if_false
        type_label = "Категория" if unknown.mapping_type == "category" else "Продавец"

        ttk.Label(
            frame,
            text=f"{type_label}:",
            font=("TkDefaultFont", 9, "bold")
        ).grid(row=0, column=0, sticky="w", padx=(0, 5))

        # Original value (what we're mapping FROM)
        value_label = ttk.Label(
            frame,
            text=unknown.original_value,
            wraplength=250
        )
        value_label.grid(row=0, column=1, sticky="w", padx=(0, 20))

        # === LEARNING: tk.StringVar ===
        # StringVar is a "bindable" variable - changes propagate to/from widgets.
        # [C++/Qt] Like QLineEdit::text() property with signals/slots
        # [JS] Like Vue's reactive refs or React's useState
        #
        # Two-way binding:
        # - When user types in Entry, StringVar updates
        # - When you call var.set("x"), Entry updates
        ttk.Label(frame, text="Тег:").grid(row=0, column=2, padx=(0, 5))

        tag_var = tk.StringVar(value=unknown.suggested_tag)

        # === LEARNING: ttk.Combobox ===
        # Dropdown/select widget
        # textvariable = the StringVar bound to this widget
        # values = list of options
        # state="readonly" = can't type, only select
        tag_combo = ttk.Combobox(
            frame,
            textvariable=tag_var,
            values=self.config.output_tags,
            width=15,
            state="readonly"
        )
        tag_combo.grid(row=0, column=3, padx=(0, 10))

        # Purpose entry (only for vendors)
        purpose_var = tk.StringVar(value=unknown.suggested_purpose)

        if unknown.mapping_type == "vendor":
            ttk.Label(frame, text="Название:").grid(row=0, column=4, padx=(0, 5))
            purpose_entry = ttk.Entry(frame, textvariable=purpose_var, width=20)
            purpose_entry.grid(row=0, column=5)

        # Store references to variables for later retrieval
        # === LEARNING: Dict with mixed value types ===
        # Using Any type hint allows any value type in the dict
        self.entries[index] = {
            "unknown": unknown,
            "tag": tag_var,       # StringVar
            "purpose": purpose_var  # StringVar
        }

    def _save(self):
        """Save mappings and close."""
        # === LEARNING: dict.values() iteration ===
        # Iterate over values only (not keys)
        # [C++] Like: for (const auto& [key, value] : map) { ... }
        for entry in self.entries.values():
            unknown = entry["unknown"]

            # .get() retrieves the current value from StringVar
            tag = entry["tag"].get()
            purpose = entry["purpose"].get()

            if unknown.mapping_type == "category":
                self.config.add_category_mapping(unknown.original_value, tag)
            else:
                # Use original value as purpose if not specified
                if not purpose:
                    purpose = unknown.original_value
                self.config.add_vendor_override(unknown.original_value, tag, purpose)

        self.saved = True
        self._cleanup()

    def _skip(self):
        """Close without saving."""
        self.saved = False
        self._cleanup()

    def _cleanup(self):
        """
        Clean up and close dialog.

        === LEARNING: Cleanup pattern ===
        Important to unbind global events to prevent errors after window closes.
        [C++] Like cleanup in destructor
        """
        # Unbind mousewheel to prevent errors after close
        # Without this, mousewheel events would try to scroll destroyed canvas
        self.dialog.unbind_all("<MouseWheel>")

        # destroy() closes the window and frees resources
        # [C++/Qt] Like: delete dialog; or dialog->deleteLater();
        self.dialog.destroy()
