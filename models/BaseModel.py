import sqlalchemy as sa
from models.DB import Base, lock_and_release, connect_and_close
from sqlalchemy.orm import Session


class BaseModel(Base):
    __abstract__ = True

    id = sa.Column(sa.Integer, autoincrement=True, primary_key=True)

    @classmethod
    @lock_and_release
    async def add(cls, vals: dict, s: Session = None):
        s.execute(sa.insert(cls).values(vals).prefix_with("OR IGNORE"))

    @classmethod
    @lock_and_release
    async def update(cls, row_id: int, update_dict: dict, s: Session = None):
        s.query(cls).filter_by(id=row_id).update(update_dict)

    @lock_and_release
    async def update_one(self, update_dict: dict, s: Session = None):
        s.query(type(self)).filter_by(id=self.id).update(update_dict)
        # for k, v in update_dict.items():
        #     setattr(self, k, v)

    @classmethod
    @lock_and_release
    async def delete(cls, attr, val, s: Session = None):
        s.query(cls).filter(getattr(cls, attr) == val).delete()

    @lock_and_release
    async def delete_one(self, s: Session = None):
        s.query(type(self)).filter_by(id=self.id).delete()

    @classmethod
    @connect_and_close
    def get_by(
        cls,
        conds: dict = None,
        all: bool = False,
        last: bool = False,
        s: Session = None,
    ):
        if conds:
            res = s.scalars(
                sa.select(cls).where(
                    sa.and_(*[getattr(cls, attr) == val for attr, val in conds.items()])
                )
            )
            if all:
                return res.all()
            if last:
                all_res = res.all()
                if all_res:
                    return all_res[-1]
            return res.first()
        res = s.scalars(sa.select(cls))
        if last:
            all_res = res.all()
            if all_res:
                return all_res[-1]
        return res.all()
