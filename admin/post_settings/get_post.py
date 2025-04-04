from telegram import Update, Chat, InlineKeyboardMarkup, InlineKeyboardButton, Bot
from telegram.ext import (
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from custom_filters import Admin
from common.keyboards import build_back_to_home_page_button, build_back_button
from common.back_to_home_page import back_to_admin_home_page_handler
import models
from Config import Config
from start import admin_command
from admin.post_settings.post_settings import post_settings_handler


POST_ID, POST_OPTION, NEW_VAL = range(3)


async def get_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        back_buttons = [
            build_back_button("back_to_post_settings"),
            build_back_to_home_page_button()[0],
        ]
        posts = models.Post.get_by()
        if not posts:
            await update.callback_query.answer(
                text="ليس لديك منشورات ❗️",
                show_alert=True,
            )
            return ConversationHandler.END
        text = f"أرسل رقم المنشور من <b>{posts[0].id}</b> إلى <b>{posts[-1].id}</b>"
        if update.callback_query.data.startswith("back"):
            await update.callback_query.delete_message()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )

        else:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=InlineKeyboardMarkup(back_buttons),
            )
        return POST_ID


async def get_post_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.message:
            post_id = int(update.message.text)
        else:
            post_id = int(update.callback_query.data.split("_")[-1])
        res = await refresh_post(
            post_id=post_id,
            chat_id=update.effective_chat.id,
            bot=context.bot,
        )
        if not res:
            await update.message.reply_text(text="لم يتم العثور على المنشور ❗️"),
            return
        return POST_OPTION


async def delete_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        post_id = int(update.callback_query.data.split("_")[-1])
        await models.Post.delete(attr="id", val=post_id)
        await update.callback_query.answer(
            text=f"تم حذف المنشور رقم {post_id} بنجاح ✅",
            show_alert=True,
        )
        await update.callback_query.edit_message_reply_markup()
        back_buttons = [
            build_back_button("back_to_post_settings"),
            build_back_to_home_page_button()[0],
        ]
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=("أرسل رقم منشور آخر\n" "للإلغاء اضغط /admin"),
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return POST_ID


async def choose_update_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        await update.callback_query.answer()
        post_id = int(update.callback_query.data.split("_")[-1])
        context.user_data["post_id"] = post_id
        update_option = update.callback_query.data.split("_")[-2]
        back_buttons = [
            build_back_button(f"back_to_choose_update_option_{post_id}"),
            build_back_to_home_page_button()[0],
        ]
        context.user_data["update_option"] = update_option
        if update_option == "video":
            text = "أرسل الفيديو الجديد 🎞"
        elif update_option == "photo":
            text = "أرسل الصورة الجديدة 🖼"
        else:
            text = "أرسل النص الجديد 📝"
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return NEW_VAL


back_to_choose_update_option = get_post_id


async def get_new_val(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        post_id = context.user_data["post_id"]
        post = models.Post.get_by(conds={"id": post_id})
        update_option = context.user_data["update_option"]
        if update_option == "video" and update.message.video:
            sent_post = await context.bot.send_video(
                chat_id=Config.POSTS_CHANNEL,
                video=update.message.video,
                caption=post.text,
            )
            await post.update_one(
                update_dict={
                    "video": sent_post.video.file_id,
                }
            )
        elif update_option == "photo" and update.message.photo:
            sent_post = await context.bot.send_photo(
                chat_id=Config.POSTS_CHANNEL,
                photo=update.message.photo[-1],
                caption=post.text,
            )
            await post.update_one(
                update_dict={
                    "photo": sent_post.photo[-1].file_id,
                }
            )
        elif (
            update_option == "text"
            and not update.message.photo
            and not update.message.video
        ):
            await post.update_one(
                update_dict={
                    "text": update.message.text_html,
                }
            )
        await update.message.reply_text(text="تم التعديل بنجاح ✅")
        await refresh_post(
            post_id=post_id,
            chat_id=update.effective_chat.id,
            bot=context.bot,
        )
        return POST_OPTION


async def refresh_post(post_id: int, chat_id: int, bot: Bot):
    post = models.Post.get_by(conds={"id": post_id})
    if not post:
        return False
    post_options_keyboard = [
        [
            InlineKeyboardButton(
                text="تعديل النص 📝",
                callback_data=f"update_post_text_{post_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="حذف ✖️",
                callback_data=f"delete_post_{post_id}",
            ),
        ],
        build_back_button("back_to_get_post_id"),
        build_back_to_home_page_button()[0],
    ]
    if post.photo or post.video:
        post_options_keyboard.insert(
            1,
            [
                InlineKeyboardButton(
                    text="تعديل الصورة 🖼" if post.photo else "تعديل الفيديو 🎞",
                    callback_data=f"update_post_{'photo' if post.photo else 'video'}_{post_id}",
                )
            ],
        )
    if post.photo:
        await bot.send_photo(
            chat_id=chat_id,
            photo=post.photo,
            caption=post.text,
            reply_markup=InlineKeyboardMarkup(post_options_keyboard),
        )
    elif post.video:
        await bot.send_video(
            chat_id=chat_id,
            video=post.video,
            caption=post.text,
            reply_markup=InlineKeyboardMarkup(post_options_keyboard),
        )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text=post.text,
            reply_markup=InlineKeyboardMarkup(post_options_keyboard),
        )
    return True


back_to_get_post_id = get_post


get_post_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            get_post,
            "^get_post$",
        ),
    ],
    states={
        POST_ID: [
            MessageHandler(
                filters=filters.Regex("^[0-9]+$"),
                callback=get_post_id,
            ),
        ],
        POST_OPTION: [
            CallbackQueryHandler(
                choose_update_option,
                "^update_post",
            ),
            CallbackQueryHandler(
                delete_post,
                "^delete_post",
            ),
        ],
        NEW_VAL: [
            MessageHandler(
                filters=filters.PHOTO
                | filters.VIDEO
                | (filters.TEXT & ~filters.COMMAND),
                callback=get_new_val,
            )
        ],
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
        post_settings_handler,
        CallbackQueryHandler(
            back_to_choose_update_option, "^back_to_choose_update_option"
        ),
        CallbackQueryHandler(back_to_get_post_id, "^back_to_get_post_id"),
    ],
)
