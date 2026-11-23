"""Небольшой пример обработки номенклатурных позиций."""

from dataclasses import dataclass
import re


@dataclass
class RawPosition:
    id: str
    name: str
    unit: str = ""
    article: str = ""


@dataclass
class Position:
    id: str
    original_name: str
    normalized_name: str
    normalized_unit: str
    match_key: str


class NormalizationService:
    """Приводит названия и единицы измерения к общему виду."""

    units = {
        "шт.": "шт",
        "штука": "шт",
        "штуки": "шт",
        "кг.": "кг",
        "килограмм": "кг",
        "литр": "л",
    }

    def clean_text(self, value):
        value = value.lower().replace("ё", "е").strip()
        value = re.sub(r"[^а-яa-z0-9\\s/-]", " ", value)
        return re.sub(r"\\s+", " ", value).strip()

    def normalize(self, item):
        name = self.clean_text(item.name)
        unit = self.clean_text(item.unit)
        unit = self.units.get(unit, unit)
        article = self.clean_text(item.article)

        key = "|".join(part for part in (name, unit, article) if part)

        return Position(
            id=item.id,
            original_name=item.name,
            normalized_name=name,
            normalized_unit=unit,
            match_key=key,
        )


def find_duplicates(positions):
    """Ищет позиции с одинаковым ключом."""
    result = []
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            if positions[i].match_key == positions[j].match_key:
                result.append((positions[i].id, positions[j].id))
    return result


def main():
    items = [
        RawPosition("1", " Болт М8, оцинкованный ", "шт.", "А-10"),
        RawPosition("2", "болт м8 оцинкованный", "штука", "А-10"),
        RawPosition("3", "Гайка М8", "шт", "А-11"),
    ]

    service = NormalizationService()
    positions = [service.normalize(item) for item in items]
    duplicates = find_duplicates(positions)

    print("Результат нормализации:")
    for position in positions:
        print(position.id, "-", position.match_key)

    print("\\nНайденные совпадения:")
    for pair in duplicates:
        print(pair[0], "и", pair[1])


if __name__ == "__main__":
    main()
