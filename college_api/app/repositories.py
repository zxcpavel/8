from sqlalchemy import select
from sqlalchemy.orm import Session


class Repository:
    """Слой доступа к данным: универсальные операции над любой моделью."""

    def __init__(self, db: Session, model):
        self.db, self.model = db, model

    def list(self):
        return list(self.db.scalars(select(self.model).order_by(self.model.id)))

    def get(self, id: int):
        return self.db.get(self.model, id)

    def add(self, data: dict):
        obj = self.model(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj, data: dict):
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj):
        self.db.delete(obj)
        self.db.commit()
