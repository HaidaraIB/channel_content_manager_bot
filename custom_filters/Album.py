from telegram import (
    Update,
)

from telegram.ext.filters import (
    BaseFilter,
)

class Album(BaseFilter):

    def filter(self, update:Update):
        try:
            return update.message.photo and update.message.media_group_id
        except:
            return False