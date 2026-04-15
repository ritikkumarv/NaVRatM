from fastapi import APIRouter
from app.schemas import VerifyUserRequest, VerifyUserResponse
from app.services.aadhar_services import verify_aadhaar
from app.services.pan_service import verify_pan
from app.services.itr_service import get_itr_data
from app.services.blacklist_service import check_blacklist

router = APIRouter(tags=["Verification"])


@router.post("/verify-user", response_model=VerifyUserResponse)
def verify_user(data: VerifyUserRequest):
    pan_data = verify_pan(data.pan)
    aadhaar_data = verify_aadhaar(data.aadhaar)
    itr_data = get_itr_data(data.pan)
    blacklist_data = check_blacklist(data.pan)
    return VerifyUserResponse(
        **pan_data,
        **aadhaar_data,
        **itr_data,
        **blacklist_data,
    )
