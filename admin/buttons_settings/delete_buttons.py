from telegram import Chat, Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler
from custom_filters import Admin
import models
from common.keyboards import build_back_to_home_page_button, build_back_button
from common.back_to_home_page import back_to_admin_home_page_handler
from admin.buttons_settings.common import build_buttons_settings_keyboard
from admin.buttons_settings.buttons_settings import buttons_settings_handler
from start import admin_command


DELETE_BUTTON = range(1)


async def delete_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == Chat.PRIVATE and Admin().filter(update):
        if update.callback_query.data.startswith("button"):
            await models.Button.delete(
                attr="id", val=int(update.callback_query.data.replace("button_", ""))
            )
            await update.callback_query.answer(
                text="تم حذف الزر بنجاح ✅",
                show_alert=True,
            )

        keyboard = models.Button.build_keyboard(with_ids=True)
        if not keyboard:
            if update.callback_query.data == "delete_buttons":
                await update.callback_query.answer(
                    text="ليس لديك أزرار ❗️",
                    show_alert=True,
                )
            else:
                keyboard = build_buttons_settings_keyboard()
                keyboard.append(build_back_to_home_page_button()[0])

                await update.callback_query.edit_message_text(
                    text="إعدادات الأزرار ⌨️",
                    reply_markup=InlineKeyboardMarkup(keyboard),
                )
            return ConversationHandler.END

        keyboard.append(build_back_button("back_to_buttons_settings"))
        keyboard.append(build_back_to_home_page_button()[0])
        await update.callback_query.edit_message_text(
            text="اختر الزر لحذفه",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return DELETE_BUTTON


delete_buttons_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            delete_buttons,
            "^delete_buttons$",
        ),
    ],
    states={
        DELETE_BUTTON: [
            CallbackQueryHandler(
                delete_buttons,
                "^button_",
            ),
        ],
    },
    fallbacks=[
        admin_command,
        back_to_admin_home_page_handler,
        buttons_settings_handler,
    ],
)
