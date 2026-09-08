"""Strict Card JSON loading."""
from pathlib import Path
import json

from card_definition import (
    CardDefinition,
    CardType,
    CharacterDefinition,
    ClimaxDefinition,
    EventDefinition,
)
from card_value_rules import (
    CardValueError,
    validate_card_icons,
    validate_card_number,
    validate_card_type,
    validate_color,
    validate_cost,
    validate_level,
    validate_name,
    validate_power,
    validate_soul,
    validate_traits,
    validate_trigger_icons,
)

CARD_ROOT = Path(__file__).resolve().parent / "cards"

TYPE_FIELD = "card_type"
COMMON_FIELDS = frozenset({"card_number", "name", "color", "trigger_icons"})
CHARACTER_FIELDS = frozenset({"level", "cost", "power", "soul", "traits", "card_icons"})
EVENT_FIELDS = frozenset({"level", "cost", "card_icons"})
CLIMAX_FIELDS = frozenset()

CARD_FIELDS_BY_TYPE = {
    CardType.CHARACTER: frozenset({TYPE_FIELD}) | COMMON_FIELDS | CHARACTER_FIELDS,
    CardType.EVENT: frozenset({TYPE_FIELD}) | COMMON_FIELDS | EVENT_FIELDS,
    CardType.CLIMAX: frozenset({TYPE_FIELD}) | COMMON_FIELDS | CLIMAX_FIELDS,
}


class CardLoadError(ValueError):
    def __init__(self, message: str, *, path: Path | str | None = None, card_number: str | None = None):
        self.path = Path(path) if path is not None else None
        self.card_number = card_number
        context = []
        if self.path is not None:
            context.append(str(self.path))
        if card_number is not None:
            context.append(f"card_number: {card_number}")
        super().__init__("\n".join((*context, message)) if context else message)


class CardJsonSyntaxError(CardLoadError):
    pass


class DuplicateCardFieldError(CardLoadError):
    pass


class CardSchemaError(CardLoadError):
    def __init__(
        self,
        *,
        missing_fields=(),
        unexpected_fields=(),
        path=None,
        card_number=None,
        card_type=None,
    ):
        self.missing_fields = tuple(sorted(missing_fields))
        self.unexpected_fields = tuple(sorted(unexpected_fields))
        self.card_type = card_type

        lines = [f"{card_type.value} Card schema error" if card_type is not None else "Card schema error"]
        if self.missing_fields:
            lines.append("缺少字段: " + ", ".join(self.missing_fields))
        if self.unexpected_fields:
            lines.append("未定义字段: " + ", ".join(self.unexpected_fields))
        super().__init__("\n".join(lines), path=path, card_number=card_number)


class InvalidCardValueError(CardLoadError):
    def __init__(self, value_error: CardValueError, *, path=None, card_number=None):
        self.field_name = value_error.field_name
        self.value = value_error.value
        super().__init__(str(value_error), path=path, card_number=card_number)


class _DuplicateJsonField(ValueError):
    def __init__(self, fields):
        self.fields = tuple(fields)
        super().__init__(", ".join(self.fields))


def _unique_object_pairs(pairs):
    result = {}
    duplicates = []
    for key, value in pairs:
        if key in result and key not in duplicates:
            duplicates.append(key)
        result[key] = value
    if duplicates:
        raise _DuplicateJsonField(duplicates)
    return result


def _parse_card_json(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text, object_pairs_hook=_unique_object_pairs)
    except _DuplicateJsonField as exc:
        raise DuplicateCardFieldError(
            "重复字段: " + ", ".join(exc.fields),
            path=path,
        ) from exc
    except json.JSONDecodeError as exc:
        raise CardJsonSyntaxError(
            f"JSON 语法错误: {exc.msg} (line {exc.lineno}, column {exc.colno})",
            path=path,
        ) from exc

    if type(data) is not dict:
        raise CardSchemaError(
            unexpected_fields=("<top-level-non-object>",),
            path=path,
        )
    return data


def _card_number_context(data) -> str | None:
    value = data.get("card_number")
    return value if type(value) is str else None


def _read_card_type(data: dict, path: Path) -> CardType:
    card_number = _card_number_context(data)
    if TYPE_FIELD not in data:
        raise CardSchemaError(
            missing_fields=(TYPE_FIELD,),
            path=path,
            card_number=card_number,
        )
    try:
        return validate_card_type(data[TYPE_FIELD])
    except CardValueError as exc:
        raise InvalidCardValueError(exc, path=path, card_number=card_number) from exc


def _validate_exact_schema(data: dict, card_type: CardType, path: Path):
    expected = CARD_FIELDS_BY_TYPE[card_type]
    actual = frozenset(data)
    missing = expected - actual
    unexpected = actual - expected
    if missing or unexpected:
        raise CardSchemaError(
            missing_fields=missing,
            unexpected_fields=unexpected,
            path=path,
            card_number=_card_number_context(data),
            card_type=card_type,
        )


def _validated_common(data: dict, path: Path) -> dict:
    card_number_context = _card_number_context(data)
    try:
        return {
            "card_number": validate_card_number(data["card_number"]),
            "name": validate_name(data["name"]),
            "color": validate_color(data["color"]),
            "trigger_icons": validate_trigger_icons(data["trigger_icons"]),
        }
    except CardValueError as exc:
        raise InvalidCardValueError(exc, path=path, card_number=card_number_context) from exc


def _validated_character_specific(data: dict, path: Path) -> dict:
    try:
        return {
            "level": validate_level(data["level"]),
            "cost": validate_cost(data["cost"]),
            "power": validate_power(data["power"]),
            "soul": validate_soul(data["soul"]),
            "traits": validate_traits(data["traits"]),
            "card_icons": validate_card_icons(data["card_icons"]),
        }
    except CardValueError as exc:
        raise InvalidCardValueError(exc, path=path, card_number=_card_number_context(data)) from exc


def _validated_event_specific(data: dict, path: Path) -> dict:
    try:
        return {
            "level": validate_level(data["level"]),
            "cost": validate_cost(data["cost"]),
            "card_icons": validate_card_icons(data["card_icons"]),
        }
    except CardValueError as exc:
        raise InvalidCardValueError(exc, path=path, card_number=_card_number_context(data)) from exc


def load_card_definition(path: Path | str) -> CardDefinition:
    path = Path(path)
    data = _parse_card_json(path)
    card_type = _read_card_type(data, path)
    _validate_exact_schema(data, card_type, path)
    common = _validated_common(data, path)

    if card_type is CardType.CHARACTER:
        return CharacterDefinition(**common, **_validated_character_specific(data, path))
    if card_type is CardType.EVENT:
        return EventDefinition(**common, **_validated_event_specific(data, path))
    if card_type is CardType.CLIMAX:
        return ClimaxDefinition(**common)
    raise AssertionError("unreachable CardType")


def load_card(relative_path: Path | str) -> CardDefinition:
    relative_path = Path(relative_path)
    if relative_path.is_absolute():
        raise ValueError("卡片路径必须相对于 cards/ 目录")
    root = CARD_ROOT.resolve()
    resolved = (CARD_ROOT / relative_path).resolve()
    if resolved != root and root not in resolved.parents:
        raise ValueError("卡片路径不能离开 cards/ 目录")
    return load_card_definition(resolved)
