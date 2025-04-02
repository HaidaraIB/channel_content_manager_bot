from telegram import Update
from telegram.ext.filters import UpdateFilter
import models


class User(UpdateFilter):
    def filter(self, update: Update):
        return not models.User.get_by(
            conds={
                "user_id": update.effective_user.id,
            }
        ).is_admin
