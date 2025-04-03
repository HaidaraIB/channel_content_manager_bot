from telegram import Update, Chat, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler
from custom_filters import Admin
from common.keyboards import build_back_to_home_page_button


async def post_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = [
            [
                InlineKeyboardButton(
                    text="إضافة ➕",
                    callback_data="add_posts",
                ),
                InlineKeyboardButton(
                    text="عرض منشور 👓",
                    callback_data="get_post",
                ),
            ],
            build_back_to_home_page_button()[0],
        ]
        await update.callback_query.edit_message_text(
            text="إعدادات المنشورات 📝",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


post_settings_handler = CallbackQueryHandler(
    post_settings,
    "^(back_to_)?post_settings$",
)
