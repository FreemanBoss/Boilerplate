from fastapi import APIRouter
from api.v1.auth.route import auth
from api.v1.seed.route import seed
from api.v1.superadmin.route import superadmin
from api.v1.user.route import user
from api.v1.notification.route import notification
from api.v1.verification_request.route import verification
from api.v1.role_and_permission.route import role_and_permission
from api.v1.profile.route import profiles
from api.v1.sticker.route import sticker
from api.v1.place.route import place
from api.v1.events.route import event
from api.v1.date_invitation.route import date
from api.v1.two_fa.route import two_factor
from api.v1.trusted_devices.route import trusted_devices

api_version_one = APIRouter(prefix="/api/v1")

two_factor.include_router(trusted_devices)
auth.include_router(two_factor)


api_version_one.include_router(auth)
api_version_one.include_router(user)
api_version_one.include_router(seed)
api_version_one.include_router(superadmin)
api_version_one.include_router(notification)
api_version_one.include_router(role_and_permission)
api_version_one.include_router(verification)
api_version_one.include_router(profiles)
api_version_one.include_router(sticker)
api_version_one.include_router(place)
api_version_one.include_router(event)
api_version_one.include_router(date)
