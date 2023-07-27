from fastapi import APIRouter, Request, Depends, HTTPException, Body
from fastapi.encoders import jsonable_encoder

from flohmarkt.models.report import ReportSchema
from flohmarkt.models.user import UserSchema
from flohmarkt.models.item import ItemSchema
from flohmarkt.auth import get_current_user

router = APIRouter()

@router.post("/")
async def add_report(report: ReportSchema = Body(...), current_user: UserSchema = Depends(get_current_user)):
    report = jsonable_encoder(report)
    report["reporter_user_id"] = current_user["id"]
    new_report = await ReportSchema.add(report, current_user)
    return new_report


@router.get("/reportees")
async def get_reportees(req: Request, limit=25, skip=0, current_user : UserSchema = Depends(get_current_user)):
    if not (current_user["moderator"] or current_user["admin"]):
        raise HTTPException(status_code=403, detail="Only mod and admin may do this")

    reportees = await ReportSchema.get_reportees(limit, skip)

    item_ids = [r[1] for r in reportees if r[0] == "item"]
    user_ids = [r[1] for r in reportees if r[0] == "user"]

    items = {}
    users = {}
    for i in await ItemSchema.retrieve_many(item_ids):
        items[i["id"]] = i
    for u in await UserSchema.retrieve_many(user_ids):
        users[u["id"]] = u

    result = []


    for r in reportees:
        if r[0] == "item" and r[1] in items:
            result.append(items[r[1]])
        elif r[0] == "user" and r[1] in users:
            result.append(users[r[1]])

    return result

@router.get("/{reportee}")
async def get_reports(req: Request, reportee: str, current_user: UserSchema = Depends(get_current_user)):
    if not (current_user["moderator"] or current_user["admin"]):
        raise HTTPException(status_code=403, detail="Only mod and admin may do this")
    return await ReportSchema.retrieve_by_reportee(reportee)
