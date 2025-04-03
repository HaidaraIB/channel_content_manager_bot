from telegram import (
    Chat,
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButtonRequestChat,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from common.back_to_home_page import back_to_admin_home_page_handler
from common.keyboards import build_admin_keyboard
from common.constants import *
from custom_filters import Admin
from admin.admin_settings.admin_settings import admin_settings_handler
from start import admin_command
import models

CHANNEL = 0


async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.answer()
        await update.callback_query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=(
                "اختر القناة التي تريد إضافتها بالضغط على الزر أدناه\n\n"
                "يمكنك إرسال الid برسالة أيضاً\n\n"
                "أو إلغاء العملية بالضغط على /admin."
            ),
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(
                            text="اختيار قناة",
                            request_chat=KeyboardButtonRequestChat(
                                request_id=6, chat_is_channel=True
                            ),
                        )
                    ]
                ],
                resize_keyboard=True,
            ),
        )
        return CHANNEL


async def get_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.effective_message.chat_shared:
            channel_id = update.effective_message.chat_shared.chat_id
        else:
            channel_id = int(update.message.text)
        try:
            channel = await context.bot.get_chat(chat_id=channel_id)
        except:
            await update.message.reply_text(
                text="لم يتم العثور على القناة ❗️",
            )
            return

        await models.Channel.add(
            vals={
                "channel_id": channel_id,
                "username": channel.username,
                "name": (
                    channel.title
                    if channel.title
                    else (
                        (channel.first_name + channel.last_name)
                        if channel.last_name
                        else channel.first_name
                    )
                ),
            }
        )

        await update.message.reply_text(
            text="تمت إضافة القناة بنجاح ✅",
            reply_markup=ReplyKeyboardRemove(),
        )
        await update.message.reply_text(
            text=HOME_PAGE_TEXT,
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


add_channel_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=add_channel,
            pattern="^add_channel$",
        ),
    ],
    states={
        CHANNEL: [
            MessageHandler(
                filters=filters.Regex("^-?[0-9]+$"),
                callback=get_channel,
            ),
            MessageHandler(
                filters=filters.StatusUpdate.CHAT_SHARED,
                callback=get_channel,
            ),
        ]
    },
    fallbacks=[
        admin_settings_handler,
        admin_command,
        back_to_admin_home_page_handler,
    ],
)
