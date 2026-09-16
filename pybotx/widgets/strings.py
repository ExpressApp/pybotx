from typing import Final


MONTHS: Final[dict[int, str]] = {
    1: "Янв",
    2: "Фев",
    3: "Мар",
    4: "Апр",
    5: "Май",
    6: "Июн",
    7: "Июл",
    8: "Авг",
    9: "Сен",
    10: "Окт",
    11: "Ноя",
    12: "Дек",
}

WEEKDAYS: Final[tuple[str, ...]] = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")

SELECTED_VALUE_LABEL: Final[str] = "{label} {selected_val}"
CHOOSE_LABEL: Final[str] = "Выбрать"
FILL_LABEL: Final[str] = "Ввести"
EMPTY: Final[str] = "[Пусто]"

LEFT_ARROW: Final[str] = "⬅️"
RIGHT_ARROW: Final[str] = "➡️"
UP_ARROW: Final[str] = "⬆️"
DOWN_ARROW: Final[str] = "⬇️"

CHECKBOX_CHECKED: Final[str] = "☑"
CHECKBOX_UNCHECKED: Final[str] = "☐"
CHECK_MARK: Final[str] = "✔️"
ENVELOPE: Final[str] = "✉️"
PENCIL: Final[str] = "✏️"
CROSS_MARK: Final[str] = "❌"

CAL_DATE_SELECTED: Final[str] = "Дата выбрана"
SELECT_DATE: Final[str] = "Выберите дату"

EMPTY_MSG_SYMBOL: Final[str] = "-"
