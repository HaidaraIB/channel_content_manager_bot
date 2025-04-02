from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes
from telegram.constants import ChatType
import uuid
from common.keyboards import build_request_buttons
from Config import Config
import logging
import os
import models

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
if Config.OWNER_ID != 755501092:
    logging.getLogger("httpx").setLevel(logging.WARNING)


def check_hidden_keyboard(context: ContextTypes.DEFAULT_TYPE):
    if (
        not context.user_data.get("request_keyboard_hidden", None)
        or not context.user_data["request_keyboard_hidden"]
    ):
        context.user_data["request_keyboard_hidden"] = False
        request_buttons = build_request_buttons()
        reply_markup = ReplyKeyboardMarkup(request_buttons, resize_keyboard=True)
    else:
        reply_markup = ReplyKeyboardRemove()
    return reply_markup


def uuid_generator():
    return uuid.uuid4().hex


def create_folders():
    os.makedirs("data", exist_ok=True)


async def invalid_callback_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == ChatType.PRIVATE:
        await update.callback_query.answer("انتهت صلاحية هذا الزر")


def get_lang(user_id: int):
    return models.User.get_by(conds={"user_id": user_id}).lang.name
