from telegram import Update, Message
from telegram.ext import ContextTypes, MessageHandler, filters
from Config import Config
import models


async def store_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await add_one_post(post=update.effective_message)


async def add_one_post(post: Message):
    if post.photo:
        await models.Post.add(
            vals={
                "photo": post.photo[-1].file_id,
                "text": post.caption_html,
            }
        )
    elif post.video:
        await models.Post.add(
            vals={
                "video": post.video,
                "text": post.caption_html,
            }
        )
    else:
        await models.Post.add(
            vals={
                "text": post.text_html,
            }
        )


store_post_handler = MessageHandler(
    filters=(
        filters.Chat(chat_id=Config.POSTS_CHANNEL)
        & (filters.PHOTO | filters.VIDEO | (filters.TEXT & ~filters.COMMAND))
    ),
    callback=store_post,
)
