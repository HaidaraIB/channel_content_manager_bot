from telegram import Update
from telegram.ext import CallbackQueryHandler, InvalidCallbackData
from start import start_command, admin_command
from common.common import invalid_callback_data, create_folders
from common.back_to_home_page import (
    back_to_admin_home_page_handler,
    back_to_user_home_page_handler,
)
from common.error_handler import error_handler
from common.force_join import check_joined_handler

from user.user_calls import *
from user.user_settings import *

from admin.admin_calls import *
from admin.admin_settings import *
from admin.broadcast import *
from admin.ban import *
from admin.post_settings import *
from admin.channels_settings import *
from admin.scheduling import *
from admin.buttons_settings import *

from jobs import reset_daily_posted_count, post_job

from models import create_tables
from datetime import time
from MyApp import MyApp
from common.constants import *


def main():
    create_folders()
    create_tables()

    app = MyApp.build_app()

    app.add_handler(
        CallbackQueryHandler(
            callback=invalid_callback_data, pattern=InvalidCallbackData
        )
    )

    app.add_handler(delete_buttons_handler)
    app.add_handler(add_buttons_handler)
    app.add_handler(buttons_settings_handler)

    app.add_handler(update_scheduling_handler)
    app.add_handler(change_state_handler)
    app.add_handler(change_scheduling_type_handler)
    app.add_handler(scheduling_handler)

    app.add_handler(add_channel_handler)
    app.add_handler(delete_channel_handler)
    app.add_handler(channels_settings_handler)

    app.add_handler(add_posts_handler)
    app.add_handler(get_post_handler)
    app.add_handler(post_settings_handler)

    app.add_handler(user_settings_handler)
    app.add_handler(change_lang_handler)

    # ADMIN SETTINGS
    app.add_handler(show_admins_handler)
    app.add_handler(add_admin_handler)
    app.add_handler(remove_admin_handler)
    app.add_handler(admin_settings_handler)

    app.add_handler(broadcast_message_handler)

    app.add_handler(check_joined_handler)

    app.add_handler(ban_unban_user_handler)

    app.add_handler(admin_command)
    app.add_handler(start_command)
    app.add_handler(find_id_handler)
    app.add_handler(hide_ids_keyboard_handler)
    app.add_handler(back_to_user_home_page_handler)
    app.add_handler(back_to_admin_home_page_handler)

    app.add_handler(show_popup_handler)

    app.job_queue.run_daily(
        callback=reset_daily_posted_count,
        time=time(0, tzinfo=TIMEZONE),
        job_kwargs={
            "id": "reset_daily_posted_count",
            "misfire_grace_time": None,
            "coalesce": True,
            "replace_existing": True,
        },
    )

    app.add_error_handler(error_handler)

    app.run_polling(allowed_updates=Update.ALL_TYPES)
