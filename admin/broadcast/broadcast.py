from telegram import Chat, Update, InlineKeyboardMarkup, error
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from common.keyboards import build_admin_keyboard, build_back_to_home_page_button
from admin.broadcast.common import build_broadcast_keyboard, send_to, build_done_button
from common.back_to_home_page import back_to_admin_home_page_handler
from start import start_command, admin_command
import models
import asyncio
from custom_filters import Admin

(
    THE_MESSAGE,
    SEND_TO,
    ENTER_USERS,
) = range(3)


async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.edit_message_text(
            text="أرسل الرسالة",
            reply_markup=InlineKeyboardMarkup(build_back_to_home_page_button()),
        )
        return THE_MESSAGE


async def get_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.message:
            context.user_data["the_message"] = update.message
            await update.message.reply_text(
                text="هل تريد إرسال الرسالة إلى:",
                reply_markup=build_broadcast_keyboard(),
            )
        else:
            await update.callback_query.edit_message_text(
                text="هل تريد إرسال الرسالة إلى:",
                reply_markup=build_broadcast_keyboard(),
            )
        return SEND_TO


back_to_the_message = broadcast_message


async def choose_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.callback_query.data == "specific_users":
            context.user_data["specific_users"] = set()
            await update.callback_query.edit_message_text(
                text="قم بإرسال آيديات المستخدمين الذين تريد إرسال الرسالة لهم عند الانتهاء اضغط تم الانتهاء",
                reply_markup=build_done_button(),
            )
            return ENTER_USERS

        elif update.callback_query.data == "all_users":
            users = models.User.get_by(
                conds={
                    "is_admin": False,
                    "is_banned": False,
                },
                all=True,
            )
        elif update.callback_query.data == "all_admins":
            users = models.User.get_by(
                conds={
                    "is_admin": True,
                    "is_banned": False,
                },
                all=True,
            )
        elif update.callback_query.data == "everyone":
            users = models.User.get_by(
                conds={
                    "is_banned": False,
                },
                all=True,
            )

        asyncio.create_task(
            send_to(
                users=users,
                context=context,
            )
        )
        await update.callback_query.edit_message_text(
            text="يقوم البوت بإرسال الرسائل الآن، يمكنك متابعة استخدامه بشكل طبيعي",
            reply_markup=build_admin_keyboard(),
        )

        return ConversationHandler.END


back_to_send_to = get_message


async def enter_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        user_id = int(update.message.text)
        punch_line = "تابع مع باقي الآيديات واضغط تم الانتهاء عند الانتهاء"

        try:
            await context.bot.get_chat(chat_id=user_id)
        except error.TelegramError:
            await update.message.reply_text(
                text=(
                    "لم يتم العثور على المستخدم، ربما لم يبدأ محادثة مع البوت بعد ❗️\n"
                    + punch_line
                ),
                reply_markup=build_done_button(),
            )
            return

        context.user_data["specific_users"].add(user_id)
        await update.message.reply_text(
            text="تم العثور على المستخدم ✅\n" + punch_line,
            reply_markup=build_done_button(),
        )
        return ENTER_USERS


async def done_entering_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.edit_message_text(
            text="يقوم البوت بإرسال الرسائل الآن، يمكنك متابعة استخدامه بشكل طبيعي",
            reply_markup=build_admin_keyboard(),
        )
        asyncio.create_task(
            send_to(users=context.user_data["specific_users"], context=context)
        )
        return ConversationHandler.END


broadcast_message_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            broadcast_message,
            "^broadcast$",
        )
    ],
    states={
        THE_MESSAGE: [
            MessageHandler(
                filters=(filters.TEXT & ~filters.COMMAND)
                | filters.PHOTO
                | filters.VIDEO
                | filters.AUDIO
                | filters.VOICE
                | filters.CAPTION,
                callback=get_message,
            )
        ],
        SEND_TO: [
            CallbackQueryHandler(
                callback=choose_users,
                pattern="^((all)|(specific))_((users)|(admins))$|^everyone$",
            )
        ],
        ENTER_USERS: [
            CallbackQueryHandler(
                done_entering_users,
                "^done_entering_users$",
            ),
            MessageHandler(
                filters=filters.Regex("^\d+$"),
                callback=enter_users,
            ),
        ],
    },
    fallbacks=[
        back_to_admin_home_page_handler,
        start_command,
        admin_command,
        CallbackQueryHandler(back_to_the_message, "^back_to_the_message$"),
        CallbackQueryHandler(back_to_send_to, "^back_to_send_to$"),
    ],
)
