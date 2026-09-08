"""Value validation and normalization for CardDefinition data."""
from enum import Enum
from typing import TypeVar

from card_definition import CardColor, CardIcon, CardType, TriggerIcon


class CardValueError(ValueError):
    """One Card Information value is invalid."""

    def __init__(self, field_name: str, message: str, *, value: object = None):
        self.field_name = field_name
        self.value = value
        super().__init__(f'字段 "{field_name}": {message}')


EnumT = TypeVar("EnumT", bound=Enum)


def _require_exact_type(field_name: str, value: object, expected_type: type):
    if type(value) is not expected_type:
        raise CardValueError(
            field_name,
            f"期望 {expected_type.__name__}，实际 {type(value).__name__}，值: {value!r}",
            value=value,
        )
    return value


def _validate_enum(field_name: str, value: object, enum_type: type[EnumT]) -> EnumT:
    _require_exact_type(field_name, value, str)
    try:
        return enum_type(value)
    except ValueError as exc:
        legal = ", ".join(member.value for member in enum_type)
        raise CardValueError(
            field_name,
            f"非法值 {value!r}；合法值: {legal}",
            value=value,
        ) from exc


def _validate_string_list(field_name: str, value: object) -> tuple[str, ...]:
    _require_exact_type(field_name, value, list)
    result = []
    for index, item in enumerate(value):
        if type(item) is not str:
            raise CardValueError(
                field_name,
                f"第 {index} 项期望 str，实际 {type(item).__name__}，值: {item!r}",
                value=value,
            )
        result.append(item)
    return tuple(result)


def _validate_enum_list(field_name: str, value: object, enum_type: type[EnumT]) -> tuple[EnumT, ...]:
    _require_exact_type(field_name, value, list)
    result = []
    for index, item in enumerate(value):
        if type(item) is not str:
            raise CardValueError(
                field_name,
                f"第 {index} 项期望 str，实际 {type(item).__name__}，值: {item!r}",
                value=value,
            )
        try:
            result.append(enum_type(item))
        except ValueError as exc:
            legal = ", ".join(member.value for member in enum_type)
            raise CardValueError(
                field_name,
                f"第 {index} 项非法值 {item!r}；合法值: {legal}",
                value=value,
            ) from exc
    return tuple(result)


def validate_card_type(value: object) -> CardType:
    return _validate_enum("card_type", value, CardType)


def validate_card_number(value: object) -> str:
    # TODO: add stricter Card Number rules only after they are confirmed.
    return _require_exact_type("card_number", value, str)


def validate_name(value: object) -> str:
    # TODO: add further name constraints only after they are confirmed.
    return _require_exact_type("name", value, str)


def validate_color(value: object) -> CardColor:
    return _validate_enum("color", value, CardColor)


def validate_trigger_icons(value: object) -> tuple[TriggerIcon, ...]:
    return _validate_enum_list("trigger_icons", value, TriggerIcon)


def validate_card_icons(value: object) -> tuple[CardIcon, ...]:
    return _validate_enum_list("card_icons", value, CardIcon)


def validate_traits(value: object) -> tuple[str, ...]:
    return _validate_string_list("traits", value)


def validate_level(value: object) -> int:
    # TODO: add legal range constraints after official values are confirmed.
    return _require_exact_type("level", value, int)


def validate_cost(value: object) -> int:
    # TODO: add legal range constraints after official values are confirmed.
    return _require_exact_type("cost", value, int)


def validate_power(value: object) -> int:
    # TODO: add legal range constraints after official values are confirmed.
    return _require_exact_type("power", value, int)


def validate_soul(value: object) -> int:
    # TODO: add legal range constraints after official values are confirmed.
    return _require_exact_type("soul", value, int)
