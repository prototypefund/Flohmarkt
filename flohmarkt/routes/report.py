from fastapi import HTTPException, Body

from flohmarkt.report import ReportSchema

router = APIRouter()

@router.post("/")
async def add_report(report: ReportSchema = Body(...), current_user: UserSchema = Depends(get_current_user)):
    report["user_id"] = current_user["id"]
    new_report = await ReportSchema.add(report, current_user)
    return new_report

@router.get("/")
async def get_reports(req: Request, limit=25, skip=0 current_user: UserSchema = Depends(get_current_user)):
    if not (current_user["moderator"] or current_user["admin"]):
        raise HTTPException(status_code=403, detail="Only mod and admin may do this")
    return await ReportSchema.retrieve(limit, skip)
