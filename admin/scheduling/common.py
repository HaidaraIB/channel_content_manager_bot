from telegram import InlineKeyboardButton
from telegram.ext import ContextTypes
import models
from datetime import datetime
from common.constants import *
from common.common import format_float, format_datetime
from apscheduler.job import Job


def get_next_post_datetime(
    context: ContextTypes.DEFAULT_TYPE,
    scheduling_type: str,
) -> datetime:
    next_run_time: datetime = None
    if scheduling_type == "regular":
        for i in range(1, 4):
            post_job: Job = context.job_queue.scheduler.get_job(f"{i}_regular_post_job")
            if post_job:
                next_run_time = post_job.next_run_time
                break
    else:
        random_post_job: Job = context.job_queue.scheduler.get_job("random_post_job")
        if random_post_job:
            next_run_time = random_post_job.next_run_time
    return next_run_time.astimezone(tz=TIMEZONE) if next_run_time else None


def stringify_scheduling_info(context: ContextTypes.DEFAULT_TYPE):
    scheduling_info = models.Scheduling.get_by(conds={"id": 1})
    s_type_en_to_ar = {"regular": "منتظم 📏", "random": "عشوائي 🎲"}
    s_state_en_to_ar = {False: "متوقف ▶️", True: "قيد التشغيل ⏸"}
    last_post = models.Post.get_by(last=True)
    next_post_datetime = get_next_post_datetime(
        context=context, scheduling_type=scheduling_info.scheduling_type
    )
    now = datetime.now(TIMEZONE).date()
    remaining_days = (
        30
        if scheduling_info.start_date > now
        else 30 - (now - scheduling_info.start_date).days
    )
    return (
        "إعدادات الجدولة 🗓\n\n"
        f"المنشور التالي: <b>{context.bot_data.get('current_post_id', 'غير محدد')}</b>\n"
        f"نظام الجدولة: <b>{s_type_en_to_ar[scheduling_info.scheduling_type]}</b>\n"
        f"عدد المنشورات في اليوم: <b>{scheduling_info.daily_posts_count}</b>\n"
        f"حالة الجدولة: <b>{s_state_en_to_ar[scheduling_info.is_on]}</b>\n"
        f"تاريخ البدء:\n<b>{scheduling_info.start_date}</b>\n\n"
        "▼ الإحصائيات:\n"
        f"- المنجز: <b>{scheduling_info.next_post_id - 1}/{last_post.id} ({format_float(((scheduling_info.next_post_id - 1) * 100)/last_post.id)}%)</b>\n"
        f"- المنجز اليوم: <b>{scheduling_info.daily_posted_count}/{scheduling_info.daily_posts_count} ({format_float((scheduling_info.daily_posted_count *100)/scheduling_info.daily_posts_count)}%)</b>\n"
        f"- المتبقي: <b>{remaining_days} يوم</b>\n"
        f"- التالي: المنشور <b>#{scheduling_info.next_post_id}</b> عند\n<b>{format_datetime(next_post_datetime) if next_post_datetime else 'غير محدد'}</b>\n\n"
        f"<i><b>تنبيه</b></i>: لن يتم تطبيق التعديلات حتى اليوم التالي ❗️"
    )


def build_scheduling_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                text="بدء الجدولة ▶️",
                callback_data="start_scheduling",
            ),
            InlineKeyboardButton(
                text="إيقاف الجدولة ⏸",
                callback_data="pause_scheduling",
            ),
        ],
        [
            InlineKeyboardButton(
                text="منتظم 📐",
                callback_data="regular",
            ),
            InlineKeyboardButton(
                text="عشوائي 🎲",
                callback_data="random",
            ),
        ],
        [
            InlineKeyboardButton(
                text="عدد المنشورات اليومي 🔢",
                callback_data="daily_posts_count",
            ),
        ],
        [
            InlineKeyboardButton(
                text="تاريخ البدء 📅",
                callback_data="start_date",
            ),
        ],
    ]
    return keyboard
