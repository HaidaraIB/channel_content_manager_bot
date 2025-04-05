import sqlalchemy as sa
from models.BaseModel import BaseModel
from datetime import date
from common.constants import *


class Scheduling(BaseModel):
    __tablename__ = "scheduling"

    scheduling_type = sa.Column(sa.String, default="regular")
    daily_posts_count = sa.Column(sa.Integer, default=1)
    start_date = sa.Column(sa.Date, default=date(2100, 1, 1))
    next_post_id = sa.Column(sa.Integer, default=1)
    daily_posted_count = sa.Column(sa.Integer, default=0)
    is_on = sa.Column(sa.Boolean, default=False)
