from telegram.ext import ContextTypes
import models
from common.constants import *
from datetime import time, datetime


SCHEDULING_JOBS_NAME = "scheduling_jobs"


async def schedule_daily_random_posting(context: ContextTypes.DEFAULT_TYPE):
    scheduling_info = models.Scheduling.get_by(conds={"id": 1})
    context.job_queue.run_repeating(
        callback=do_post,
        name=SCHEDULING_JOBS_NAME,
        interval=24 * 60 * 60 / scheduling_info.daily_posts_count,
        job_kwargs={
            "id": "random_post_job",
            "misfire_grace_time": None,
            "coalesce": True,
            "replace_existing": True,
        },
    )


async def schedule_daily_regular_posting(context: ContextTypes.DEFAULT_TYPE):
    scheduling_info = models.Scheduling.get_by(conds={"id": 1})
    interval = 60 / (scheduling_info.daily_posts_count / 12) * 60
    context.job_queue.run_repeating(
        callback=do_post,
        interval=interval,
        first=time(hour=1, tzinfo=TIMEZONE),
        last=time(hour=5, tzinfo=TIMEZONE),
        name=SCHEDULING_JOBS_NAME,
        job_kwargs={
            "id": "1_regular_post_job",
            "misfire_grace_time": None,
            "coalesce": True,
            "replace_existing": True,
        },
    )
    context.job_queue.run_repeating(
        callback=do_post,
        interval=interval,
        first=time(hour=9, tzinfo=TIMEZONE),
        last=time(hour=13, tzinfo=TIMEZONE),
        name=SCHEDULING_JOBS_NAME,
        job_kwargs={
            "id": "2_regular_post_job",
            "misfire_grace_time": None,
            "coalesce": True,
            "replace_existing": True,
        },
    )
    context.job_queue.run_repeating(
        callback=do_post,
        interval=interval,
        first=time(hour=17, tzinfo=TIMEZONE),
        last=time(hour=21, tzinfo=TIMEZONE),
        name=SCHEDULING_JOBS_NAME,
        job_kwargs={
            "id": "3_regular_post_job",
            "misfire_grace_time": None,
            "coalesce": True,
            "replace_existing": True,
        },
    )


async def reset_daily_posted_count(context: ContextTypes.DEFAULT_TYPE):
    scheduling_info = models.Scheduling.get_by(conds={"id": 1})
    await scheduling_info.update_one(update_dict={"daily_posted_count": 0})


async def do_post(context: ContextTypes.DEFAULT_TYPE):
    scheduling_info = models.Scheduling.get_by(conds={"id": 1})

    if not scheduling_info.is_on:
        return

    next_post_id = scheduling_info.next_post_id
    post = models.Post.get_by(conds={"id": next_post_id})
    while not post:
        next_post_id += 1
        post = models.Post.get_by(conds={"id": next_post_id})

    channels = models.Channel.get_by()
    for channel in channels:
        if post.photo:
            await context.bot.send_photo(
                chat_id=channel.channel_id,
                photo=post.photo,
                caption=post.text,
            )
        elif post.video:
            await context.bot.send_video(
                chat_id=channel.channel_id,
                video=post.video,
                caption=post.text,
            )
        else:
            await context.bot.send_message(
                chat_id=channel.channel_id,
                text=post.text,
            )

    await scheduling_info.update_one(
        update_dict={
            "next_post_id": next_post_id + 1,
            "daily_posted_count": scheduling_info.daily_posted_count + 1,
        }
    )


async def reschedule(context: ContextTypes.DEFAULT_TYPE):
    scheduling_info = models.Scheduling.get_by(conds={"id": 1})
    remove_existing_jobs(context)

    if scheduling_info.scheduling_type == "regular":
        context.job_queue.run_daily(
            callback=schedule_daily_regular_posting,
            time=time(hour=0, tzinfo=TIMEZONE),
            name=SCHEDULING_JOBS_NAME,
            job_kwargs={
                "id": "schedule_daily_regular_posting_job",
                "misfire_grace_time": None,
                "coalesce": True,
                "replace_existing": True,
            },
        )
    else:
        context.job_queue.run_daily(
            callback=schedule_daily_random_posting,
            time=time(hour=0, tzinfo=TIMEZONE),
            name=SCHEDULING_JOBS_NAME,
            job_kwargs={
                "id": "schedule_daily_random_posting_job",
                "misfire_grace_time": None,
                "coalesce": True,
                "replace_existing": True,
            },
        )


def remove_existing_jobs(context: ContextTypes.DEFAULT_TYPE):
    scheduling_jobs = context.job_queue.get_jobs_by_name(SCHEDULING_JOBS_NAME)
    for job in scheduling_jobs:
        job.schedule_removal()
