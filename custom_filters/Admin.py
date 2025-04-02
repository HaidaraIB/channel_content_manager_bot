from telegram import Update
from telegram.ext.filters import UpdateFilter
import models


class Admin(UpdateFilter):
    def filter(self, update: Update):
        return models.User.get_by(
            conds={
                "user_id": update.effective_user.id,
            },
        ).is_admin
