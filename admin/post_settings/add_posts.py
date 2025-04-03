from telegram import Update, Chat, InlineKeyboardMarkup, error
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from custom_filters import Admin
from common.keyboards import (
    build_back_to_home_page_button,
    build_back_button,
    build_admin_keyboard,
)
from common.back_to_home_page import back_to_admin_home_page_handler
import models
from Config import Config
from start import admin_command
from admin.post_settings.post_settings import post_settings_handler
import asyncio

POSTS = range(1)


add_post_lock = asyncio.Lock()


async def add_posts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        back_buttons = [
            build_back_button("back_to_post_settings"),
            build_back_to_home_page_button()[0],
        ]
        context.user_data["added_posts_counter"] = 0
        context.user_data["first_added_post_id"] = 1
        last_post = models.Post.get_by(last=True)
        if last_post:
            context.user_data["first_added_post_id"] = last_post.id + 1
        await update.callback_query.edit_message_text(
            text="أرسل المنشورات وعند الانتهاء أرسل كلمة <b>تم</b>",
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return POSTS


async def get_posts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        try:
            await add_post_lock.acquire()
            await add_one_post(update, context)
        except:
            import traceback
            traceback.print_exc()
        finally:
            add_post_lock.release()
        context.user_data["added_posts_counter"] += 1


async def add_one_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        post = await context.bot.send_photo(
            chat_id=Config.POSTS_CHANNEL,
            photo=update.message.photo[-1],
            caption=update.message.caption_html,
        )
        await models.Post.add(
            vals={
                "photo": post.photo[-1].file_id,
                "text": post.caption_html,
            }
        )
    elif update.message.video:
        post = await context.bot.send_video(
            chat_id=Config.POSTS_CHANNEL,
            video=update.message.video,
            caption=update.message.caption_html,
        )
        await models.Post.add(
            vals={
                "video": post.video,
                "text": post.caption_html,
            }
        )
    else:
        post = await context.bot.send_message(
            chat_id=Config.POSTS_CHANNEL,
            text=update.message.text_html,
        )
        await models.Post.add(
            vals={
                "text": post.text_html,
            }
        )


async def done_sending_posts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if add_post_lock.locked():
            await update.message.reply_text(
                text="الرجاء الانتظار، عملية حفظ المنشورات ما تزال مستمرة ❗️"
            )
            return
        last_post = models.Post.get_by(last=True)
        if context.user_data["added_posts_counter"] > 1:
            text = f"تمت إضافة <b>{context.user_data['added_posts_counter']}</b> منشور مرقمة من <b>{context.user_data['first_added_post_id']}</b> إلى <b>{last_post.id}</b> بنجاح ✅"
        else:
            text = f"تمت إضافة <b>{context.user_data['added_posts_counter']}</b> منشور رقمه <b>{last_post.id}</b> بنجاح ✅"
        await update.message.reply_text(text=text, reply_markup=build_admin_keyboard())
        return ConversationHandler.END


add_posts_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            add_posts,
            "^add_posts$",
        ),
    ],
    states={
        POSTS: [
            MessageHandler(
                filters=filters.Regex("^تم$"),
                callback=done_sending_posts,
            ),
            MessageHandler(
                filters=filters.PHOTO
                | filters.VIDEO
                | (filters.TEXT & ~filters.COMMAND),
                callback=get_posts,
            ),
        ],
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
        post_settings_handler,
    ],
)
