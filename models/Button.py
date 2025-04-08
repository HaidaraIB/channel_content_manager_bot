import sqlalchemy as sa
from sqlalchemy.orm import Session
from models.BaseModel import BaseModel
from models.DB import connect_and_close

from telegram import InlineKeyboardButton


class Button(BaseModel):
    __tablename__ = "buttons"

    button_type = sa.Column(sa.String)
    text = sa.Column(sa.String)
    popup_text = sa.Column(sa.String)
    share_text = sa.Column(sa.String)
    telegram_link = sa.Column(sa.String)
    row = sa.Column(sa.Integer)
    col = sa.Column(sa.Integer)

    @classmethod
    @connect_and_close
    def get_max_position(cls, dimension: str, s: Session = None):
        """
        Get the maximum row or column value

        Args:
            dimension: Either 'row' or 'col'
            session: Optional SQLAlchemy session

        Returns:
            int: Maximum value found (0 if no records)
        """
        if dimension not in ("row", "col"):
            raise ValueError("Dimension must be either 'row' or 'col'")

        try:
            result = s.execute(sa.select(sa.func.max(getattr(cls, dimension))))
            max_val = result.scalar()
            return max_val if max_val is not None else -1
        except Exception as e:
            s.rollback()
            raise e

    @classmethod
    @connect_and_close
    def build_keyboard(cls, with_ids: bool = False, s: Session = None):
        buttons = s.query(Button).order_by(Button.row, Button.col).all()

        if not buttons:
            return

        # Create a dictionary to organize buttons by row
        keyboard_dict = {}

        for button in buttons:
            # Create the appropriate button type
            if button.button_type == "telegram_link":
                btn = InlineKeyboardButton(
                    text=button.text,
                    url=(
                        f"https://t.me/{button.telegram_link}" if not with_ids else None
                    ),
                    callback_data=f"button_{button.id}" if with_ids else None,
                )
            elif button.button_type == "popup":
                btn = InlineKeyboardButton(
                    text=button.text,
                    callback_data=(
                        f"button_{button.id}"
                        if with_ids
                        else f"popup:{button.popup_text}"
                    ),
                )
            else:
                continue  # Skip unknown button types

            # Organize by row
            if button.row not in keyboard_dict:
                keyboard_dict[button.row] = {}
            keyboard_dict[button.row][button.col] = btn

        # Convert to the required list of lists format
        keyboard = []
        for row in sorted(keyboard_dict.keys()):
            # Get buttons in column order and create row
            row_buttons = [
                keyboard_dict[row][col] for col in sorted(keyboard_dict[row].keys())
            ]
            keyboard.append(row_buttons)

        return keyboard
