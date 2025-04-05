from telegram import Update, Chat, BotCommandScopeChat, Bot
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    Application,
    ConversationHandler,
)
import models
from custom_filters import Admin
from common.decorators import (
    check_if_user_banned_dec,
    add_new_user_dec,
    check_if_user_member_decorator,
)
from common.keyboards import build_user_keyboard, build_admin_keyboard
from common.common import check_hidden_keyboard, get_lang
from common.lang_dicts import TEXTS
from common.constants import *
from Config import Config
from datetime import datetime


async def inits(app: Application):
    bot: Bot = app.bot
    owner = await bot.get_chat(chat_id=Config.OWNER_ID)
    await models.User.add(
        vals={
            "user_id": owner.id,
            "username": owner.username if owner.username else "",
            "name": owner.full_name,
            "is_admin": True,
        },
    )
    await models.Scheduling.add(vals={"id": 1})


async def set_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    st_cmd = ("start", "start command")
    commands = [st_cmd]
    if Admin().filter(update):
        commands.append(("admin", "admin command"))
    await context.bot.set_my_commands(
        commands=commands, scope=BotCommandScopeChat(chat_id=update.effective_chat.id)
    )


@add_new_user_dec
@check_if_user_banned_dec
# @check_if_user_member_decorator
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE:
        await set_commands(update, context)
        lang = get_lang(update.effective_user.id)
        await update.message.reply_text(
            text=TEXTS[lang]["welcome_msg"],
            reply_markup=build_user_keyboard(lang),
        )
        return ConversationHandler.END


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await set_commands(update, context)
        await update.message.reply_text(
            text="أهلاً بك...",
            reply_markup=check_hidden_keyboard(context),
        )

        await update.message.reply_text(
            text="تعمل الآن كآدمن 🕹",
            reply_markup=build_admin_keyboard(),
        )
        return ConversationHandler.END


start_command = CommandHandler(command="start", callback=start)
admin_command = CommandHandler(command="admin", callback=admin)
