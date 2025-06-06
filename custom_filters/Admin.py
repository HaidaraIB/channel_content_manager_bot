from telegram import Update
from telegram.ext.filters import UpdateFilter
import models


class Admin(UpdateFilter):
    def filter(self, update: Update):
        try:
            return models.User.get_by(
                conds={
                    "user_id": (
                        update.effective_user.id
                        if update.effective_user
                        else update.effective_sender.id
                    ),
                },
            ).is_admin
        except:
            return False
            
