from telegram import Chat, Update, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
from custom_filters import Admin
from common.keyboards import build_back_to_home_page_button, build_back_button
from common.constants import *
from common.back_to_home_page import back_to_admin_home_page_handler
from admin.scheduling.common import stringify_scheduling_info, build_scheduling_keyboard
from datetime import date, datetime
from start import admin_command
from jobs import remove_existing_jobs, reschedule
import models

DAILY_POSTS_COUNT, START_DATE = range(2)


async def scheduling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        keyboard = [
            *build_scheduling_keyboard(),
            build_back_to_home_page_button()[0],
        ]
        if update.message:
            await update.message.reply_text(
                text=stringify_scheduling_info(context=context),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            await update.callback_query.edit_message_text(
                text=stringify_scheduling_info(context=context),
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        return ConversationHandler.END


async def choose_scheduling_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        scheduling_info = models.Scheduling.get_by(conds={"id": 1})
        back_buttons = [
            build_back_button("back_to_scheduling"),
            build_back_to_home_page_button()[0],
        ]
        if update.callback_query.data == "daily_posts_count":
            text = (
                f"أرسل عدد المنشورات اليومية الجديد\n"
                f"العدد الحالي: <b>{scheduling_info.daily_posts_count if scheduling_info else 'غير محدد'}</b>\n"
            )
            RET = DAILY_POSTS_COUNT
        elif update.callback_query.data == "start_date":
            text = (
                f"أرسل تاريخ البدء بالتنسيق\n"
                "<code>YYYY-MM-DD</code>\n"
                f"التاريخ الحالي: <b>{scheduling_info.start_date if scheduling_info else 'غير محدد'}</b>"
            )
            RET = START_DATE
        await update.callback_query.edit_message_text(
            text=text,
            reply_markup=InlineKeyboardMarkup(back_buttons),
        )
        return RET


async def get_daily_posts_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        daily_posts_count = int(update.message.text)
        await models.Scheduling.update(
            row_id=1, update_dict={"daily_posts_count": daily_posts_count}
        )
        await update.message.reply_text(text="تم تعديل عدد المنشورات اليومي بنجاح ✅")
        return await scheduling(update, context)


async def get_start_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):

        scheduling_info = models.Scheduling.get_by(conds={"id": 1})

        start_date = date.fromisoformat(update.message.text)
        now = datetime.now(tz=TIMEZONE).date()
        if now >= start_date:
            await update.message.reply_text(text="الرجاء إرسال تاريخ في المستقبل ❗️")
            return

        # guard for unchanged start_date cases to prevent unnecessary reschedule
        if scheduling_info.start_date != start_date:
            await scheduling_info.update_one(update_dict={"start_date": start_date})
            remove_existing_jobs(
                context
            )  # we must remove_jobs right away to stop posting immediately
            context.job_queue.run_once(
                callback=reschedule,
                when=datetime(
                    start_date.year,
                    start_date.month,
                    start_date.day,
                    0,
                    0,
                    tzinfo=TIMEZONE,
                ),
                name="reschedule",
                job_kwargs={
                    "id": "reschedule",
                    "misfire_grace_time": None,
                    "coalesce": True,
                    "replace_existing": True,
                },
            )

        await update.message.reply_text(text="تم تعديل تاريخ البدء بنجاح ✅")

        return await scheduling(update, context)


async def change_scheduling_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        new_scheduling_type = update.callback_query.data
        scheduling_info = models.Scheduling.get_by(conds={"id": 1})
        # guard for unchanged scheduling_type cases to prevent unnecessary reschedule
        if scheduling_info.scheduling_type != new_scheduling_type:
            await models.Scheduling.update(
                row_id=1, update_dict={"scheduling_type": new_scheduling_type}
            )
            await reschedule(context)

        await update.callback_query.answer(
            text="تمت العملية بنجاح ✅",
            show_alert=True,
        )
        await scheduling(update, context)


async def change_state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.callback_query.data.startswith("pause"):
            await models.Scheduling.update(row_id=1, update_dict={"is_on": False})
            text = "تم إيقاف الجدولة ⏸"
        else:
            await models.Scheduling.update(row_id=1, update_dict={"is_on": True})
            text = "تم تشغيل الجدولة ▶️"
        await update.callback_query.answer(
            text=text,
            show_alert=True,
        )
        await scheduling(update, context)


scheduling_handler = CallbackQueryHandler(scheduling, "^(back_to_)?scheduling$")
update_scheduling_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            choose_scheduling_option,
            "^start_date$|^daily_posts_count$",
        ),
    ],
    states={
        DAILY_POSTS_COUNT: [
            MessageHandler(
                filters=filters.Regex("^[0-9]+$"),
                callback=get_daily_posts_count,
            ),
        ],
        START_DATE: [
            MessageHandler(
                filters=filters.Regex(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"),
                callback=get_start_date,
            ),
        ],
    },
    fallbacks=[
        scheduling_handler,
        admin_command,
        back_to_admin_home_page_handler,
    ],
)
change_scheduling_type_handler = CallbackQueryHandler(
    change_scheduling_type,
    "^((regular)|(random))$",
)
change_state_handler = CallbackQueryHandler(
    change_state,
    "^((start)|(pause))_scheduling$",
)
