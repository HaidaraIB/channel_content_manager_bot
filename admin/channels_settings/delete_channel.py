from telegram import Chat, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler
from start import admin_command
from common.keyboards import build_back_button, build_back_to_home_page_button
from common.back_to_home_page import back_to_admin_home_page_handler
from custom_filters import Admin
import models
from common.constants import *
from admin.channels_settings.channels_settings import (
    channels_settings_handler,
    build_channels_settings_keyboard,
)

CHANNEL = 0


async def delete_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        data = update.callback_query.data.split("_")[-1]
        if data[1:].isnumeric():
            channel = models.Channel.get_by(
                conds={
                    "channel_id": int(data),
                },
            )
            await channel.delete_one()

            await update.callback_query.answer(
                text="تم حذف القناة بنجاح ✅",
                show_alert=True,
            )

            channels = models.Channel.get_by()
            if not channels:
                keyboard = build_channels_settings_keyboard()
                keyboard.append(build_back_to_home_page_button()[0])
                await update.callback_query.edit_message_text(
                    text="إعدادات القنوات 📢",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                )
        channels = models.Channel.get_by()
        if not channels:
            await update.callback_query.answer(
                text="ليس لديك قنوات ❗️",
                show_alert=True,
            )
            return ConversationHandler.END

        channels_keyboard = [
            [
                InlineKeyboardButton(
                    text=ch.name,
                    callback_data=f"delete_channel_{ch.channel_id}",
                ),
            ]
            for ch in channels
        ]
        channels_keyboard.append(build_back_button("back_to_channels_settings"))
        channels_keyboard.append(build_back_to_home_page_button()[0])
        await update.callback_query.edit_message_text(
            text="اختر من القائمة أدناه القناة التي تريد حذفها.",
            reply_markup=InlineKeyboardMarkup(channels_keyboard),
        )
        return CHANNEL


delete_channel_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            callback=delete_channel,
            pattern="^delete_channel$",
        ),
    ],
    states={
        CHANNEL: [
            CallbackQueryHandler(
                delete_channel,
                "^delete_channel_-?[0-9]+$",
            ),
        ]
    },
    fallbacks=[
        channels_settings_handler,
        admin_command,
        back_to_admin_home_page_handler,
    ],
)
