import uuid
import datetime

from typing import Optional, List
from pydantic import BaseModel, Field

from flohmarkt.db import Database

class ReportSchema(BaseModel):
    type : str = "report"
    item_id : str 
    user_id : str = ""
    reporter_user_id : str = ""
    reason : str = Field(...)
    resolution : Optional[str] = ""
    creation_date : Optional[datetime.datetime] = datetime.datetime.now()

    @staticmethod
    async def retrieve_by_reportee(reportee_id : str):
        reports = []
        for report in await Database.find({"type":"report",
                                           "$or":[
                                                {"item_id" : reportee_id},
                                                {"user_id" : reportee_id}
                                            ]}):
            reports.append(report)
        return reports

    @staticmethod
    async def get_reportees(limit, skip):
        reportees = []

        break_outer = False

        dblimit = 25 
        dbskip = 0
        while True:
            if break_outer:
                break
            reports = await Database.find(
                    {"type":"report"}, 
                    sort=[{"creation_date":"desc"}],#),,
                    limit = dblimit,
                    skip = dbskip,
                    fields = ["item_id", "user_id"])
            if len(reports) < 25:
                break_outer=True
            for report in reports:

                if report["item_id"] != "" and ("item",report["item_id"]) not in reportees:
                    reportees.append(("item",report["item_id"]))
                if report["user_id"] != "" and ("user",report["user_id"]) not in reportees:
                    reportees.append(("user",report["user_id"]))

                if len(reportees) == limit + skip:
                    break_outer = True
                    break
            dbskip += dblimit
            dblimit += 25

        return reportees[-25:]

    @staticmethod
    async def retrieve(limit=25, skip=0):
        item_ids = []
        for report in await Database.find(
                {"type":"report"}, 
                sort=[{"creation_date":"desc"}],#),,
                limit = limit,
                skip = skip):
            item_ids.append(report["item_id"])
        item_ids = set(item_ids)
        results = await Database.view("reports_by_item", "reports-by-item-view", key=item_ids)
        return [result["value"] for result in results]

    @staticmethod
    async def add(data: dict, user:dict=None)->dict:
        data["type"] = "report"
        if not "id" in data:
            data["id"] = str(uuid.uuid4())
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
