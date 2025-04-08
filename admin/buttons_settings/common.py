from telegram import InlineKeyboardButton
import re


# Combined regex pattern for all button formats
BUTTON_REGEX = re.compile(
    r"^("
    r".+? - t\.me\/[^\s)]+(?:\(https:\/\/t\.me\/[^)]+\))?|"  # Telegram link
    r".+? - popup:.+|"  # Popup button
    # r".+? - share:.+|"  # Share button
    # r".+? - comments|"  # Comments button
    r"(.+? - (?:t\.me\/[^\s)]+|popup:[^&]+|share:[^&]+|comments))(?: && .+? - (?:t\.me\/[^\s)]+|popup:[^&]+|share:[^&]+|comments))+"  # Multiple buttons
    r")$",
    re.MULTILINE,
)


def parse_buttons(text: str):
    """
    Detects and parses button formats, including their row/column positions.

    Returns:
        List of buttons, each with:
        - 'type' (telegram_link, popup, share, comments)
        - 'text' (button label)
        - Additional fields (e.g., 'telegram_link', 'popup_text')
        - 'row' and 'col' (0-based indices)
    """
    buttons = []

    # Split into lines (rows)
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    for row_idx, line in enumerate(lines):
        # Split into buttons (columns) if separated by ' && '
        button_parts = [part.strip() for part in line.split("&&") if part.strip()]

        for col_idx, part in enumerate(button_parts):
            button_data = parse_single_button(part)
            if button_data:
                button_data.update({"row": row_idx, "col": col_idx})
                buttons.append(button_data)

    return buttons


def parse_single_button(button_text: str):
    """Parses a single button and returns its data (without row/col info)."""
    patterns = [
        {
            "name": "telegram_link",
            "regex": re.compile(
                r"^(.+?) - t\.me\/([^\s)]+)(?:\(https:\/\/t\.me\/[^)]+\))?$"
            ),
            "groups": ["text", "telegram_link"],
        },
        {
            "name": "popup",
            "regex": re.compile(r"^(.+?) - popup:(.+?)$"),
            "groups": ["text", "popup_text"],
        },
        # {
        #     "name": "share",
        #     "regex": re.compile(r"^(.+?) - share:(.+?)$"),
        #     "groups": ["text", "share_text"],
        # },
        # {
        #     "name": "comments",
        #     "regex": re.compile(r"^(.+?) - comments$"),
        #     "groups": ["text"],
        # },
    ]

    for pattern in patterns:
        match: re.Match = pattern["regex"].match(button_text.strip())
        if match:
            button_data = {"type": pattern["name"]}
            for i, group_name in enumerate(pattern["groups"], 1):
                button_data[group_name] = match.group(i).strip()
            return button_data

    return {"type": "unknown", "raw_text": button_text.strip()}


def build_buttons_settings_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="إضافة ➕",
                callback_data="add_buttons",
            ),
            InlineKeyboardButton(
                text="حذف ✖️",
                callback_data="delete_buttons",
            ),
        ]
    ]
    return keyboard
