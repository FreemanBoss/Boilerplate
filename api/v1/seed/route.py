from fastapi import APIRouter, status

from api.utils.task_logger import create_logger
from api.v1.seed.seed import seed_users


logger = create_logger("Auth Route")

seed = APIRouter(prefix="/seed", tags=["SEED"])


@seed.get("", status_code=status.HTTP_200_OK)
async def seed_users_to_database():
    """
    Seeds users to the database.
    """
    await seed_users()

    return {
        "status_code": 201,
        "message": "Users seeded to database. Say Thank you to Johnson for saving you the stress.",
        "data": [
            {
                "email": "firelord@gmail.com",
                "password": "Firelord1234#",
                "role": "superadmin",
            },
            {
                "email": "johnson@gmail.com",
                "password": "Johnson1234#",
                "role": "admin",
            },
            {
                "email": "jane@gmail.com",
                "password": "Jane1234#",
                "role": "admin",
            },
            {
                "email": "jackson@gmail.com",
                "password": "Jackson1234#",
                "role": "user",
            },
            {
                "email": "jayson@gmail.com",
                "password": "Jayson1234#",
                "role": "user",
            },
            {
                "email": "judason@gmail.com",
                "password": "Judason1234#",
                "role": "user",
            },
        ],
    }
