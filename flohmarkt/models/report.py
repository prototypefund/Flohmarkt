import uuid
import datetime

from typing import Optional, List
from pydantic import BaseModel, Field

from flohmarkt.db import Database

class ReportSchema(BaseModel):
    type : str = "report"
    item_id : str 
    user_id : str = ""
    reason : str = Field(...)
    resolution : Optional[str] = ""
    creation_date : Optional[datetime.datetime] = datetime.datetime.now()

    @staticmethod
    async def retrieve_by_item(item_id : str):
        reports = []
        for report in await Database.find({"type":"report", "item_id" : item_id}):
            reports.append(report)
        return reports

    @staticmethod
    async def retrieve(item_id : str, limit=25, skip=0):
        reports = []
        for report in await Database.find({"type":"report"}):
            reports.append(report)
        return reports

    @staticmethod
    async def add(data: dict, user:dict=None)->dict:
        data["type"] = "report"
        if not "id" in data:
            data["id"] = str(uuid.uuid4())
        if not "creation_date" in data or data["creation_date"] is None:
            data["creation_date"] = datetime.datetime.now()

        ins = await Database.create(data)
        new = await Database.find_one({"id":ins})
        return new

    @staticmethod
    async def update(ident: str, data: dict):
        if len(data) < 1:
            return False
        report = await Database.find_one({"id":ident})
        report.update(data)
        if report is not None:
            updated = await Database.update(
                    ident, data
            )
            if updated is not None:
                return True
            return False
