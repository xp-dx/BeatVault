from fastapi import APIRouter

router = APIRouter()


@router.get("/admin")
def admin():
    return {"message": "Hello Admin"}
