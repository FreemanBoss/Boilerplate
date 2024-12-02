import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta, timezone
from typing import Optional, List
import secrets
from jose import jwt, JWTError
from fastapi import HTTPException, status, Request

from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.user.model import User
from api.v1.user.service import user_service
from api.v1.trusted_devices.service import trusted_device_service
from api.v1.trusted_devices.schema import DeviceInfo
from api.v1.two_fa.schema import (
    TwoFactorSetupSchema, TwoFactorSetupOutputSchema,
    TwoFactorSetupOutputData, TwoFactorLoginVerifySchema,
    TwoFactorVerifySchema, TwoFactorVerifyOutputSchema,
    TwoFactorMethod
)

from api.utils.settings import Config

class TwoFactorService:
    """
    Two factor Authentication service class
    """

    def __init__(self):
        self.issuer_name = Config.APP_NAME
        
    async def setup_2fa(
        self,
        request: Request,
        schema: TwoFactorSetupSchema,
        session: AsyncSession,
        current_user: User
    ):
        """Initialize 2FA setup for a mobile device."""
    
        if not current_user.verify_password(schema.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password"
            )
        
        if current_user.two_factor_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA is already enabled"
            )
        
        # Generate secret and backup codes
        secret = await two_factor_service.generate_secret()
        backup_codes = await two_factor_service.generate_backup_codes()
        auth_uri = await mobile_2fa_service.generate_auth_uri(
            current_user.email, 
            secret
        )
        
        # Store in session temporarily
        request.session["temp_2fa_secret"] = secret
        request.session["temp_backup_codes"] = backup_codes
        request.session["device_info"] = schema.device_info.dict()
        
        two_factor_data = TwoFactorSetupOutputData(
            secret_key=secret,
            auth_uri=auth_uri,
            backup_codes=backup_codes,
            setup_method=TwoFactorMethod.TOTP
        )

        return TwoFactorSetupOutputSchema(
            message="Setup successfully initiated",
            data=two_factor_data
        )

    async def verify_login(
        self,
        request: Request,
        schema: TwoFactorLoginVerifySchema,
        session: AsyncSession
    ):
        """Verify 2FA code and optionally trust device."""
        from api.v1.auth.service import auth_service

        user_id = await two_factor_service.verify_temp_token(schema.temp_token)
        user: User = await user_service.fetch({"id": user_id}, session)
        
        if not await two_factor_service.verify_code(user.two_factor_secret, schema.code):
            # Check backup codes
            if not await two_factor_service.verify_backup_code(
                user.backup_codes, schema.code
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid verification code"
                )
            # Remove used backup code
            user.backup_codes.remove(schema.code)
            await session.commit()
        
        # Register as trusted device
        await trusted_device_service.register_trusted_device(
            user.id,
            schema.device_info,
            session
        )
        
        # TODO: Generate tokens with device info
        return await auth_service.generate_tokens_and_response(
           request,
           user,
           session
        )


    async def verify_setup(
        self,
        request: Request,
        schema: TwoFactorVerifySchema,
        session: AsyncSession,
        current_user: User
    ) -> Optional[TwoFactorVerifyOutputSchema]:
        """Verify and complete 2FA setup."""

        # Get temporary values from session
        temp_secret = request.session.get("temp_2fa_secret")
        temp_backup_codes = request.session.get("temp_backup_codes")
        device_info = request.session.get("device_info")
        
        if not all([temp_secret, temp_backup_codes, device_info]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="2FA setup session expired. Please start over."
            )
        
        # Verify the user can generate valid codes with their authenticator
        if not await two_factor_service.verify_code(temp_secret, schema.code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code. Please ensure you've properly set up your authenticator app."
            )
        
        # If verification successful, permanently store 2FA settings
        current_user.two_factor_secret = temp_secret
        current_user.backup_codes = temp_backup_codes
        current_user.two_factor_enabled = True
        current_user.two_factor_enabled_at = datetime.now(timezone.utc)
        
        # Register the device that completed setup as trusted
        await trusted_device_service.register_trusted_device(
            current_user.id,
            DeviceInfo(**device_info),
            session
        )
        
        # Clear temporary session data
        del request.session["temp_2fa_secret"]
        del request.session["temp_backup_codes"]
        del request.session["device_info"]
        
        await session.commit()

        return TwoFactorVerifyOutputSchema(
            message="2FA setup completed successfully",
            data=temp_backup_codes  # Show one final time for user to save
        )

    async def generate_backup_codes(self, count: int = 8) -> List[str]:
        """Generate backup codes for 2FA recovery."""

        return [secrets.token_hex(4).upper() for _ in range(count)]

    async def create_temp_token(self, user_id: int) -> str:
        """Create a temporary token for 2FA verification process."""

        payload = {
            "user_id": user_id,
            "type": "2fa_temp",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5)
        }
        return jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

    async def verify_temp_token(self, token: str) -> Optional[int]:
        """Verify temporary token and return user_id."""

        try:
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])
            if payload["type"] != "2fa_temp":
                raise HTTPException(status_code=400, detail="Invalid token type")
            return payload["user_id"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=400, detail="Token has expired")
        except JWTError as exc:
            raise HTTPException(status_code=400, detail="Invalid token")

    async def generate_secret(self) -> str:
        """Generate a new secret key for 2FA."""

        return pyotp.random_base32()

    async def generate_qr_code(self, email: str, secret: str) -> str:
        """Generate QR code for 2FA setup."""

        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(email, issuer_name=self.issuer_name)
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        # Create image and convert to base64
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"

    async def verify_code(self, secret: str, code: str) -> bool:
        """Verify a 2FA code."""

        if not secret or not code:
            return False
        totp = pyotp.TOTP(secret)
        return totp.verify(code)

    async def verify_backup_code(self, stored_codes: List[str], provided_code: str) -> bool:
        """Verify a backup code and remove it if valid."""

        return provided_code in stored_codes



# Mobile Devices Streamlined Services
class MobileTwoFactorService:
    """Service class for mobile devices 2FA"""

    def __init__(self):
        self.issuer_name = Config.APP_NAME

    async def generate_auth_uri(self, email: str, secret: str) -> str:
        """Generate URI for deep linking into authenticator apps."""

        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(email, issuer_name=self.issuer_name)


mobile_2fa_service = MobileTwoFactorService()
two_factor_service = TwoFactorService()