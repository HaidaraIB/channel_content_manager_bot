from telegram import Chat, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)
from custom_filters import Admin
import models
from common.keyboards import build_back_button, build_back_to_home_page_button
from common.back_to_home_page import back_to_admin_home_page_handler
from admin.buttons_settings.common import parse_buttons, BUTTON_REGEX
from admin.buttons_settings.buttons_settings import buttons_settings_handler
import re
from start import admin_command

BUTTONS, CONFIRM_ADD = range(2)


async def add_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        back_buttons = [
            build_back_button("back_to_buttons_settings"),
            build_back_to_home_page_button()[0],
        ]
        await update.callback_query.edit_message_text(
            text=(
                "اضبط الأزرار لإدراجها في لوحة المفاتيح أسفل المنشور\n"
                "أرسل رسالة منظمة على النحو التالي:\n\n"
                "<u>• أدخل زر واحد:</u>\n"
                "نص الزر - t.me/LinkExample\n\n"
                "<u>• أدخل عدة أزرار في سطر واحد:</u>\n"
                "نص الزر - t.me/LinkExample && نص الزر - t.me/LinkExample\n\n"
                "<u>• أدخل عدة أسطر من الازرار:</u>\n"
                "نص الزر - t.me/LinkExample\n"
                "نص الزر - t.me/LinkExample\n\n"
                "<u>• أدخل زر يعرض نافذة منبثقة:</u>\n"
                "نص الزر - popup: نص النافذة المنبثقة\n\n"
                "<u>• أدخل زر مشاركة:</u>\n"
                "نص الزر - share: نص للمشاركة\n\n"
                # "<u>• أدخل زر تعليقات:</u>\n"
                # "اسم الزر - comments\n"
                # "💡 <a href='https://botguide.me/s/ch-en/doc/create-posts-o7DmqM0oIB#h-comments-button'>تعرف علي كيفية القيام بذلك</a>"
            ),
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return BUTTONS


async def get_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        buttons_data = parse_buttons(update.message.text)
        context.user_data["buttons_to_add"] = buttons_data
        # Group buttons by row
        keyboard: dict[int, list] = {}
        for button_data in buttons_data:
            row = button_data["row"]
            if row not in keyboard:
                keyboard[row] = []

            # Create button based on type
            if button_data["type"] == "telegram_link":
                keyboard[row].append(
                    InlineKeyboardButton(
                        text=button_data["text"],
                        url=f"https://t.me/{button_data['telegram_link']}",
                    )
                )
            elif button_data["type"] == "popup":
                keyboard[row].append(
                    InlineKeyboardButton(
                        text=button_data["text"],
                        callback_data=f"popup:{button_data['popup_text']}",
                    )
                )
            elif button_data["type"] == "share":
                keyboard[row].append(
                    InlineKeyboardButton(
                        text=button_data["text"],
                        url=f"https://t.me/share/url?url={button_data['share_text']}",
                    )
                )
            # elif button_data["type"] == "comments":
            #     keyboard[row].append(
            #         InlineKeyboardButton(
            #             text=button_data["text"],
            #             callback_data="popup:You can't use it here!",
            #         )
            #     )

        # Convert to list of lists (preserving row order)
        keyboard_layout = [keyboard[row] for row in sorted(keyboard.keys())]

        keyboard_layout.append(build_back_button("back_to_get_buttons"))
        keyboard_layout.append(build_back_to_home_page_button()[0])

        await update.message.reply_text(
            text="تم تحليل الأزرار أدناه، لإضافتها أرسل كلمة <b>تأكيد</b>",
            reply_markup=InlineKeyboardMarkup(keyboard_layout),
        )
        return CONFIRM_ADD


back_to_get_buttons = add_buttons


async def confirm_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        max_row = models.Button.get_max_position(dimension="row")
        base_row = max_row + 1 if max_row != -1 else 0

        for button_data in context.user_data["buttons_to_add"]:
            # Calculate new position
            new_row = button_data["row"] + base_row
            new_col = button_data["col"]

            # Common fields
            vals = {
                "button_type": button_data["type"],
                "text": button_data["text"],
                "row": new_row,
                "col": new_col,
            }

            # Type-specific fields
            if button_data["type"] == "telegram_link":
                vals["telegram_link"] = button_data["telegram_link"]
            elif button_data["type"] == "popup":
                vals["popup_text"] = button_data["popup_text"]
            elif button_data["type"] == "share":
                vals["share_text"] = button_data["share_text"]
            # elif button_data["type"] == "comments":
            #     pass  # No additional fields needed

            await models.Button.add(vals=vals)
            await update.message.reply_text(
                f"تمت إضافة الزر: <b>{button_data['text']}</b> بنجاح ✅"
            )

        await update.message.reply_text("اضغط /admin للمتابعة")
        return ConversationHandler.END


add_buttons_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            add_buttons,
            "^add_buttons$",
        ),
    ],
    states={
        BUTTONS: [
            MessageHandler(
                filters=filters.Regex(BUTTON_REGEX),
                callback=get_buttons,
            )
        ],
        CONFIRM_ADD: [
            MessageHandler(
                filters=filters.Regex("^تأكيد$"),
                callback=confirm_add,
            ),
        ],
    },
    fallbacks=[
        admin_command,
        buttons_settings_handler,
        back_to_admin_home_page_handler,
        CallbackQueryHandler(back_to_get_buttons, "^back_to_get_buttons$"),
    ],
)
