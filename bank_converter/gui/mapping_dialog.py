"""Dialog for resolving unknown category/vendor mappings."""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any

from ..core.models import UnknownMapping
from ..config.manager import ConfigManager


class MappingDialog:
    """Dialog for resolving unknown category/vendor mappings."""

    def __init__(
        self,
        parent: tk.Tk,
        unknowns: List[UnknownMapping],
        config: ConfigManager
    ):
        """Initialize mapping dialog.

        Args:
            parent: Parent window.
            unknowns: List of unknown mappings to resolve.
            config: ConfigManager for saving mappings.
        """
        self.config = config
        self.unknowns = unknowns
        self.entries: Dict[int, Dict[str, Any]] = {}
        self.saved = False

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Неизвестные категории/продавцы")
        self.dialog.geometry("700x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center the dialog
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 700) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 500) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self._setup_ui()

        # Handle window close
        self.dialog.protocol("WM_DELETE_WINDOW", self._skip)

    def _setup_ui(self):
        """Create dialog UI."""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill="both", expand=True)

        # Instructions
        instructions = ttk.Label(
            main_frame,
            text="Назначьте теги для неизвестных категорий и продавцов.\n"
                 "Эти настройки будут сохранены для будущего использования.",
            wraplength=650,
            justify="left"
        )
        instructions.pack(anchor="w", pady=(0, 10))

        # Create scrollable frame
        container = ttk.Frame(main_frame)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            container, orient="vertical", command=canvas.yview
        )
        self.scroll_frame = ttk.Frame(canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas_frame = canvas.create_window(
            (0, 0), window=self.scroll_frame, anchor="nw"
        )

        # Make the frame expand with canvas
        def configure_frame(event):
            canvas.itemconfig(canvas_frame, width=event.width)

        canvas.bind("<Configure>", configure_frame)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Enable mousewheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Add entry for each unknown
        for i, unknown in enumerate(self.unknowns):
            self._create_mapping_row(i, unknown)

        # Buttons frame
        btn_frame = ttk.Frame(self.dialog, padding="10")
        btn_frame.pack(fill="x")

        ttk.Button(
            btn_frame, text="Сохранить и продолжить", command=self._save
        ).pack(side="right", padx=(5, 0))

        ttk.Button(
            btn_frame, text="Пропустить", command=self._skip
        ).pack(side="right")

    def _create_mapping_row(self, index: int, unknown: UnknownMapping):
        """Create a row for one unknown mapping.

        Args:
            index: Index of the unknown mapping.
            unknown: UnknownMapping object.
        """
        frame = ttk.Frame(self.scroll_frame)
        frame.pack(fill="x", pady=5, padx=5)

        # Type label
        type_label = "Категория" if unknown.mapping_type == "category" else "Продавец"
        ttk.Label(
            frame,
            text=f"{type_label}:",
            font=("TkDefaultFont", 9, "bold")
        ).grid(row=0, column=0, sticky="w", padx=(0, 5))

        # Value
        value_label = ttk.Label(
            frame,
            text=unknown.original_value,
            wraplength=250
        )
        value_label.grid(row=0, column=1, sticky="w", padx=(0, 20))

        # Tag dropdown
        ttk.Label(frame, text="Тег:").grid(row=0, column=2, padx=(0, 5))

        tag_var = tk.StringVar(value=unknown.suggested_tag)
        tag_combo = ttk.Combobox(
            frame,
            textvariable=tag_var,
            values=self.config.output_tags,
            width=15,
            state="readonly"
        )
        tag_combo.grid(row=0, column=3, padx=(0, 10))

        # Purpose entry (for vendors only)
        purpose_var = tk.StringVar(value=unknown.suggested_purpose)
        if unknown.mapping_type == "vendor":
            ttk.Label(frame, text="Название:").grid(row=0, column=4, padx=(0, 5))
            purpose_entry = ttk.Entry(frame, textvariable=purpose_var, width=20)
            purpose_entry.grid(row=0, column=5)

        # Store references
        self.entries[index] = {
            "unknown": unknown,
            "tag": tag_var,
            "purpose": purpose_var
        }

    def _save(self):
        """Save mappings and close."""
        for entry in self.entries.values():
            unknown = entry["unknown"]
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
        """Clean up and close dialog."""
        # Unbind mousewheel to prevent errors after close
        self.dialog.unbind_all("<MouseWheel>")
        self.dialog.destroy()
