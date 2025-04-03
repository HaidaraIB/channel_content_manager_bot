from telegram import (
    Update,
    Chat,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler
from custom_filters import Admin
from common.keyboards import build_back_button, build_back_to_home_page_button


async def channels_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = build_channels_settings_keyboard()
        keyboard.append(build_back_to_home_page_button()[0])
        await update.callback_query.edit_message_text(
            text="إعدادات القنوات 📢",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ConversationHandler.END


def build_channels_settings_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="إضافة ➕",
                callback_data="add_channel",
            ),
            InlineKeyboardButton(
                text="حذف ✖️",
                callback_data="delete_channel",
            ),
        ],
    ]
    return keyboard


channels_settings_handler = CallbackQueryHandler(
    channels_settings, "^(back_to_)?channels_settings$"
)
