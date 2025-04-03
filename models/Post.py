import sqlalchemy as sa
from common.constants import *
from models.BaseModel import BaseModel
from datetime import datetime


class Post(BaseModel):
    __tablename__ = "posts"
    photo = sa.Column(sa.String)
    video = sa.Column(sa.String)
    text = sa.Column(sa.String)
    post_date = sa.Column(sa.TIMESTAMP, server_default=str(datetime.now(TIMEZONE)))
