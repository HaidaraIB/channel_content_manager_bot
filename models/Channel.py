import sqlalchemy as sa
from models.BaseModel import BaseModel


class Channel(BaseModel):
    __tablename__ = "channels"
    channel_id = sa.Column(sa.Integer, unique=True)
    username = sa.Column(sa.String)
    name = sa.Column(sa.String)
