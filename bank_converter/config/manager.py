"""Configuration management for bank converter."""

import json
from pathlib import Path
from typing import Dict, List, Any


class ConfigManager:
    """Manages configuration loading and saving."""

    DEFAULT_CONFIG = {
        "owner": "Кирилл",
        "output_tags": [
            "Зп", "Возврат", "Транспорт", "Еда", "Развлечения",
            "Дом", "Здоровье", "Доставка", "Подарок", "Неизвестно"
        ],
        "category_mappings": {
            "Супермаркеты": "Еда",
            "Фастфуд": "Еда",
            "Рестораны": "Еда",
            "Местный транспорт": "Транспорт",
            "Аптеки": "Здоровье",
            "Тренировки": "Здоровье",
            "Цифровые товары": "Развлечения",
            "Маркетплейсы": "Неизвестно",
            "Мобильная связь": "Дом",
            "Связь": "Дом",
            "Зарплата": "Зп",
            "Бонусы": "Зп",
            "Проценты": "Зп",
            "Сервис": "Доставка",
            "Госуслуги": "Дом",
            "Ремонт и мебель": "Дом",
            "Искусство": "Развлечения",
            "Финансы": "Неизвестно",
            "Переводы": "Неизвестно"
        },
        "vendor_overrides": {
            "Boosty.to": {"tag": "Развлечения", "назначение": "Boosty"},
            "СДЭК": {"tag": "Доставка", "назначение": "СДЭК"},
            "Ozon.ru": {"tag": "Неизвестно", "назначение": "Озон"},
            "Московский метрополитен": {"tag": "Транспорт", "назначение": "Метро"},
            "ВкусВилл": {"tag": "Еда", "назначение": "ВкусВилл"},
            "Вкусно — и точка": {"tag": "Еда", "назначение": "Макдоналдс"},
            "ИгроМагаз": {"tag": "Развлечения", "назначение": "Игры"},
            "YoBody Fitness": {"tag": "Здоровье", "назначение": "Спортзал"},
            "Яндекс 360": {"tag": "Дом", "назначение": "Яндекс 360"},
            "МТС": {"tag": "Дом", "назначение": "МТС"},
            "Plati.Market": {"tag": "Развлечения", "назначение": "Игры"},
            "Ароматный мир": {"tag": "Еда", "назначение": "Ароматный мир"},
            "Магнит": {"tag": "Еда", "назначение": "Магнит"},
            "Перекрёсток": {"tag": "Еда", "назначение": "Перекрёсток"},
            "Пятёрочка": {"tag": "Еда", "назначение": "Пятёрочка"},
            "Почта России": {"tag": "Доставка", "назначение": "Почта России"},
            "DNS": {"tag": "Дом", "назначение": "DNS"},
            "Яндекс Сервисы": {"tag": "Развлечения", "назначение": "Яндекс"},
            "Альфа-Банк": {"tag": "Неизвестно", "назначение": "Альфа-Банк"},
            "Вайлдберриз Банк": {"tag": "Неизвестно", "назначение": "Wildberries"}
        },
        "skip_descriptions": [
            "Между своими счетами"
        ],
        "income_categories": [
            "Зарплата", "Бонусы", "Проценты"
        ]
    }

    def __init__(self, config_path: str = None):
        """Initialize config manager.

        Args:
            config_path: Path to config file. If None, uses default location.
        """
        self.config_path = config_path or self._default_path()
        self._data = self._load()

    def _default_path(self) -> str:
        """Get default config path (same directory as script)."""
        return str(Path(__file__).parent.parent / "mappings.json")

    def _load(self) -> Dict[str, Any]:
        """Load config from file or create default."""
        path = Path(self.config_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged = self.DEFAULT_CONFIG.copy()
                merged.update(loaded)
                # Deep merge for nested dicts
                for key in ['category_mappings', 'vendor_overrides']:
                    if key in loaded:
                        merged[key] = {**self.DEFAULT_CONFIG.get(key, {}), **loaded[key]}
                return merged
        return self.DEFAULT_CONFIG.copy()

    def save(self):
        """Save current config to file."""
        path = Path(self.config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    @property
    def owner(self) -> str:
        """Get default owner name."""
        return self._data.get("owner", "Кирилл")

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

    def add_category_mapping(self, category: str, tag: str):
        """Add or update category mapping."""
        self._data["category_mappings"][category] = tag
        self.save()

    def add_vendor_override(self, vendor: str, tag: str, purpose: str):
        """Add or update vendor override."""
        self._data["vendor_overrides"][vendor] = {
            "tag": tag,
            "назначение": purpose
        }
        self.save()

    def add_skip_description(self, description: str):
        """Add a description to skip."""
        if description not in self._data["skip_descriptions"]:
            self._data["skip_descriptions"].append(description)
            self.save()

    def remove_skip_description(self, description: str):
        """Remove a description from skip list."""
        if description in self._data["skip_descriptions"]:
            self._data["skip_descriptions"].remove(description)
            self.save()
