from sqlalchemy import Enum


notification_status_enum = Enum(
    "pending",
    "sent",
    "falied",
    name="notification_status_enum",
    create_type=False,
    check=True,
    validate_strings=True,
)

notification_type_enum = Enum(
    "alert",
    "message",
    "reminder",
    name="notification_type_enum",
    create_type=False,
    check=True,
    validate_strings=True,
)

genotype_enum = Enum(
    "AA",
    "AS",
    "SS",
    "AC",
    "SC",
    create_type=False,
    check=True,
    validate_strings=True,
    name="genotype_enum",
)

gender_type_enum = Enum(
    "male",
    "femail",
    name="gender_type_enum",
    create_type=False,
    check=True,
    validate_strings=True,
)

joining_purpose_enum = Enum(
    "date",
    "marriage",
    "friendship",
    create_type=False,
    check=True,
    validate_strings=True,
    name="joining_purpose_enum",
)
gender_type_enum = Enum(
    "male",
    "female",
    name="gender_type_enum",
    create_type=False,
    check=True,
    validate_strings=True,
)

verification_status_enum = Enum(
    "approved",
    "rejected",
    "pending",
    name="verification_status_enum",
    create_type=False,
    check=True,
    validate_strings=True,
)

subscription_plans_enum = Enum(
    "forever",
    "weekly",
    "monthly",
    "yearly",
    name="subscription_plans_enum",
    create_type=False,
    check=True,
    validate_strings=True,
)

subscription_status_enum = Enum(
    "expired",
    "active",
    name="subscription_status_enum",
    create_type=False,
    check=True,
    validate_strings=True,
)

date_invitation_status_enum = Enum(
    "pending",
    "accepted",
    "declined",
    name="date_invitation_status_enum",
    check=True,
    create_type=False,
    validate_strings=True,
)
