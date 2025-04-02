from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from common.constants import *
from admin.admin_settings.common import stringify_admin
import os
import models


async def show_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admins = models.User.get_by(
        conds={
            "is_admin": True,
        },
        all=True,
    )
    text = ""
    for admin in admins:
        if admin.id == int(os.getenv("OWNER_ID")):
            text += "<b>مالك البوت</b>\n" + stringify_admin(admin=admin)
            continue
        text += stringify_admin(admin=admin)
    text += "للمتابعة اضغط /admin"
    await update.callback_query.edit_message_text(text=text)


show_admins_handler = CallbackQueryHandler(
    callback=show_admins,
    pattern="^show_admins$",
)
