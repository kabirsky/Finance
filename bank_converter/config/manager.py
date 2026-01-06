"""
Configuration management for bank converter.

=== LEARNING: This module demonstrates ===
- Working with JSON files
- Python dictionaries (like JS objects)
- The @property decorator (getters/setters)
- File I/O with context managers
- The pathlib module for file paths
"""

# =============================================================================
# IMPORTS
# =============================================================================
import json                          # Built-in JSON handling
from pathlib import Path             # Modern path handling (better than os.path)
from typing import Dict, List, Any   # Type hints for complex types

# === LEARNING: typing module ===
# Dict[str, str] means "dictionary with string keys and string values"
# [JS] Similar to: Record<string, string> in TypeScript
# [C++] Similar to: std::map<std::string, std::string>
#
# List[str] means "list of strings"
# [JS] Similar to: string[] in TypeScript
# [C++] Similar to: std::vector<std::string>
#
# Any means "any type" - use sparingly!
# [JS] Similar to: any in TypeScript


class ConfigManager:
    """
    Manages configuration loading and saving.

    === LEARNING: Class Variables vs Instance Variables ===
    Variables defined directly in the class (like DEFAULT_CONFIG below)
    are CLASS VARIABLES - shared by all instances.

    [JS] Similar to static properties: static DEFAULT_CONFIG = {...}
    [C++] Similar to static const members
    """

    # =========================================================================
    # CLASS VARIABLE - shared by all instances
    # =========================================================================
    # === LEARNING: Python Dictionaries ===
    # Dicts are Python's key-value data structure.
    # [JS] Almost identical to JavaScript objects: { key: "value" }
    # [C++] Like std::map or std::unordered_map
    #
    # Key differences from JS:
    # - Keys are usually strings, but can be any "hashable" type
    # - Use ["key"] syntax, not .key (unless using special libraries)
    # - Use .get("key", default) to avoid KeyError on missing keys
    DEFAULT_CONFIG = {
        "owner": "Кирилл",
        # List inside dict - mixing types freely (dynamic typing!)
        "output_tags": [
            "Зп", "Возврат", "Транспорт", "Еда", "Развлечения",
            "Дом", "Здоровье", "Подарок", "Неизвестно"
        ],
        # Dict of string -> string
        "category_mappings": {
            "Супермаркеты": "Еда",
            "Фастфуд": "Еда",
            "Рестораны": "Еда",
            "Местный транспорт": "Транспорт",
            "Аптеки": "Здоровье",
            "Тренировки": "Здоровье",
            "Цифровые товары": "Развлечения",
            "Маркетплейсы": "Еда",
            "Мобильная связь": "Дом",
            "Связь": "Дом",
            "Зарплата": "Зп",
            "Бонусы": "Зп",
            "Проценты": "Зп",
            "Сервис": "Доставка",
            "Госуслуги": "Дом",
            "Ремонт и мебель": "Дом",
            "Искусство": "Развлечения",
            "Доставка": "Развлечения",
            "Финансы": "Неизвестно",
            "Переводы": "Неизвестно"
        },
        # Dict of string -> dict (nested structure)
        # [JS] Like: { "Boosty.to": { tag: "Развлечения", назначение: "Boosty" } }
        "vendor_overrides": {
            "Boosty.to": {"tag": "Развлечения", "назначение": "Boosty"},
            "СДЭК": {"tag": "Доставка", "назначение": "СДЭК"},
            "Ozon.ru": {"tag": "Дом", "назначение": "Подписка на озон"},
            "Московский метрополитен": {"tag": "Транспорт", "назначение": "Метро"},
            "ВкусВилл": {"tag": "Еда", "назначение": "ВкусВилл"},
            "Вкусно — и точка": {"tag": "Еда", "назначение": "Макдоналдс"},
            "ИгроМагаз": {"tag": "Развлечения", "назначение": "Игры"},
            "YoBody Fitness": {"tag": "Здоровье", "назначение": "Спортзал"},
            "Яндекс 360": {"tag": "Дом", "назначение": "Яндекс 360"},
            "МТС": {"tag": "Развлечения", "назначение": "Стим"},
            "Plati.Market": {"tag": "Развлечения", "назначение": "Игры"},
            "Ароматный мир": {"tag": "Еда", "назначение": "Ароматный мир"},
            "Магнит": {"tag": "Еда", "назначение": "Магнит"},
            "Перекрёсток": {"tag": "Еда", "назначение": "Перекрёсток"},
            "Пятёрочка": {"tag": "Еда", "назначение": "Пятёрочка"},
            "Почта России": {"tag": "Доставка", "назначение": "Почта России"},
            "DNS": {"tag": "Дом", "назначение": "DNS"},
            "Яндекс Сервисы": {"tag": "Развлечения", "назначение": "Яндекс"},
            "Альфа-Банк": {"tag": "Еда", "назначение": "Перекрёсток"},
            "Вайлдберриз Банк": {"tag": "Неизвестно", "назначение": "Wildberries"},
            "Дмитрий Ц.": {"tag": "Здоровье", "назначение": "Тренер"},
            "Сергей Ц.": {"tag": "Учёба", "назначение": "C++"},
            "Сая И.": {"tag": "Учёба", "назначение": "Японский"},
            "Перевод юридическому лицу": {"tag": "Здоровье", "назначение": "Психолог"},
            "Наталья С.": {"tag": "Дом", "назначение": "Аренда"},
            "Кирилл Е.": {"tag": "Еда", "назначение": "Озон"},
            "Kirill E.": {"tag": "Развлечения", "назначение": "Оплата с киргизской карты"},
            "Операция в других кредитных организациях YANDEXBANK_C2A G. MOSKVA RUS": {"tag": "Транспорт", "назначение": "Такси"}
        },
        "skip_descriptions": [
            "Между своими счетами",
            "Елизавета У."
        ],
        "income_categories": [
            "Зарплата", "Бонусы", "Проценты"
        ]
    }

    # =========================================================================
    # CONSTRUCTOR
    # =========================================================================
    def __init__(self, config_path: str = None):
        """
        Initialize config manager.

        === LEARNING: Default Arguments ===
        config_path: str = None means "if not provided, use None"
        [JS] Similar to: constructor(configPath = null)
        [C++] Similar to: ConfigManager(std::string config_path = "")

        === LEARNING: The 'or' trick ===
        `config_path or self._default_path()` returns:
        - config_path if it's truthy (not None, not empty string)
        - Otherwise, the result of _default_path()
        [JS] Same as: configPath || this._defaultPath()
        """
        # self.x = ... creates INSTANCE variables (unique to each instance)
        # [JS] Like: this.configPath = ...
        self.config_path = config_path or self._default_path()
        self._data = self._load()
        # Convention: _name means "private" (but Python doesn't enforce it!)

    # =========================================================================
    # PRIVATE METHODS (by convention, not enforced)
    # =========================================================================
    def _default_path(self) -> str:
        """
        Get default config path (same directory as script).

        === LEARNING: pathlib.Path ===
        Modern Python way to handle file paths. Better than string manipulation!

        __file__ is a special variable = path to THIS Python file
        [JS] Similar to: __filename in Node.js
        [C++] No direct equivalent; would need preprocessor macros

        Path operations:
        - Path(__file__).parent     -> directory containing this file
        - path / "subdir"           -> join paths (uses / operator!)
        - path.exists()             -> check if path exists
        - path.mkdir()              -> create directory
        """
        # Path(__file__)           -> /path/to/config/manager.py
        # .parent                  -> /path/to/config/
        # .parent                  -> /path/to/bank_converter/
        # / "mappings.json"        -> /path/to/bank_converter/mappings.json
        return str(Path(__file__).parent.parent / "mappings.json")

    def _load(self) -> Dict[str, Any]:
        """
        Load config from file or create default.

        === LEARNING: File I/O with 'with' statement ===
        """
        path = Path(self.config_path)

        # Check if file exists
        if path.exists():
            # === LEARNING: Context Manager (with statement) ===
            # The 'with' statement ensures the file is properly closed,
            # even if an exception occurs!
            #
            # [JS] Similar to try-finally, but cleaner:
            #      const f = fs.openSync(path);
            #      try { ... } finally { fs.closeSync(f); }
            #
            # [C++] Similar to RAII - resource automatically released
            #
            # 'r' = read mode, 'w' = write mode, 'a' = append mode
            # encoding='utf-8' is important for non-ASCII characters (Cyrillic!)
            with open(path, 'r', encoding='utf-8') as f:
                # json.load reads JSON from file object
                # json.loads reads JSON from string
                loaded = json.load(f)

                # === LEARNING: Dict methods ===
                # .copy() creates a SHALLOW copy (nested dicts are still shared!)
                # [JS] Similar to: { ...this.DEFAULT_CONFIG }
                merged = self.DEFAULT_CONFIG.copy()

                # .update() merges another dict into this one
                # [JS] Similar to: Object.assign(merged, loaded)
                merged.update(loaded)

                # Deep merge for nested dicts using dict unpacking
                # === LEARNING: Dict unpacking with ** ===
                # {**dict1, **dict2} creates new dict with all items from both
                # If keys conflict, dict2 wins
                # [JS] Same as: { ...dict1, ...dict2 }
                for key in ['category_mappings', 'vendor_overrides']:
                    if key in loaded:  # 'in' checks if key exists
                        merged[key] = {**self.DEFAULT_CONFIG.get(key, {}), **loaded[key]}

                return merged

        # If file doesn't exist, return copy of defaults
        return self.DEFAULT_CONFIG.copy()

    # =========================================================================
    # PUBLIC METHODS
    # =========================================================================
    def save(self):
        """
        Save current config to file.

        === LEARNING: Creating directories ===
        """
        path = Path(self.config_path)

        # Create parent directories if they don't exist
        # parents=True: create intermediate directories too
        # exist_ok=True: don't error if already exists
        # [JS] Similar to: fs.mkdirSync(dir, { recursive: true })
        path.parent.mkdir(parents=True, exist_ok=True)

        # 'w' = write mode (overwrites existing file)
        with open(path, 'w', encoding='utf-8') as f:
            # json.dump writes JSON to file object
            # ensure_ascii=False: allow non-ASCII characters (Cyrillic!)
            # indent=2: pretty-print with 2-space indentation
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    # =========================================================================
    # PROPERTIES (Getters and Setters)
    # =========================================================================
    # === LEARNING: @property Decorator ===
    # Makes a method act like a read-only attribute.
    # Access as: config.owner (not config.owner())
    #
    # [JS] Similar to:
    #      get owner() { return this._data["owner"]; }
    #
    # [C++] Similar to:
    #      std::string owner() const { return _data["owner"]; }
    #      But accessed without parentheses in Python!

    @property
    def owner(self) -> str:
        """Get default owner name."""
        # .get(key, default) returns default if key doesn't exist
        # [JS] Similar to: this._data.owner ?? "Кирилл"
        return self._data.get("owner", "Кирилл")

    # === LEARNING: @property.setter ===
    # Allows setting the property: config.owner = "New Name"
    #
    # [JS] Similar to:
    #      set owner(value) { this._data["owner"] = value; }
    @owner.setter
    def owner(self, value: str):
        """Set default owner name."""
        self._data["owner"] = value

    @property
    def output_tags(self) -> List[str]:
        """Get list of available output tags."""
        return self._data.get("output_tags", [])

    @property
    def category_mappings(self) -> Dict[str, str]:
        """Get bank category to tag mappings."""
        return self._data.get("category_mappings", {})

    @property
    def vendor_overrides(self) -> Dict[str, Dict[str, str]]:
        """Get vendor-specific overrides."""
        return self._data.get("vendor_overrides", {})

    @property
    def skip_descriptions(self) -> List[str]:
        """Get descriptions to skip (internal transfers)."""
        return self._data.get("skip_descriptions", [])

    @property
    def income_categories(self) -> List[str]:
        """Get categories that are always income."""
        return self._data.get("income_categories", [])

    # =========================================================================
    # MUTATOR METHODS
    # =========================================================================
    def add_category_mapping(self, category: str, tag: str):
        """Add or update category mapping."""
        # Dict assignment: dict[key] = value
        # [JS] Same as: this._data.category_mappings[category] = tag
        self._data["category_mappings"][category] = tag
        self.save()  # Persist immediately

    def add_vendor_override(self, vendor: str, tag: str, purpose: str):
        """Add or update vendor override."""
        # Creating a nested dict
        self._data["vendor_overrides"][vendor] = {
            "tag": tag,
            "назначение": purpose
        }
        self.save()

    def add_skip_description(self, description: str):
        """Add a description to skip."""
        # 'not in' checks if item is NOT in list
        # [JS] Like: !array.includes(item)
        if description not in self._data["skip_descriptions"]:
            # .append() adds to end of list
            # [JS] Like: array.push(item)
            self._data["skip_descriptions"].append(description)
            self.save()

    def remove_skip_description(self, description: str):
        """Remove a description from skip list."""
        # 'in' checks if item IS in list
        if description in self._data["skip_descriptions"]:
            # .remove() removes first occurrence
            # [JS] Like: array.splice(array.indexOf(item), 1)
            self._data["skip_descriptions"].remove(description)
            self.save()
