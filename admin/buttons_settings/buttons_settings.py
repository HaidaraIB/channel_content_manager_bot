from telegram import Update, Chat, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler
from custom_filters import Admin
from common.keyboards import build_back_to_home_page_button
from admin.buttons_settings.common import build_buttons_settings_keyboard


async def show_popup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer(
        text=update.callback_query.data.replace("popup:", ""),
        show_alert=True,
    )


async def buttons_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = build_buttons_settings_keyboard()
        keyboard.append(build_back_to_home_page_button()[0])
        await update.callback_query.edit_message_text(
            text="إعدادات الأزرار ⌨️",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return ConversationHandler.END


buttons_settings_handler = CallbackQueryHandler(
    buttons_settings, "^(back_to_)?buttons_settings$"
)
show_popup_handler = CallbackQueryHandler(show_popup, "^popup:")
