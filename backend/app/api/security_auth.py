"""
Security Authentication API Endpoints
Handles user authentication, MFA, and security management
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from ..core.database import get_database_manager
from ..core.logging import get_logger
from ..core.security import (
	AuthenticationMethod,
	LoginRequest,
	MFAEnableRequest,
	MFAVerifyRequest,
	Permission,
	Role,
	SecurityContext,
	SecurityLevel,
	UserCreate,
	get_security_manager,
)

logger = get_logger(__name__)
router = APIRouter()
security = HTTPBearer()


# Response Models
class AuthResponse(BaseModel):
	"""Authentication response"""

	access_token: str
	token_type: str = "bearer"
	expires_in: int
	user: Dict[str, Any]
	permissions: List[str]
	roles: List[str]


class MFAEnableResponse(BaseModel):
	"""MFA enablement response"""

	secret: str
	qr_code: str
	backup_codes: List[str]


class UserResponse(BaseModel):
	"""User response model"""

	id: int
	username: str
	email: str
	is_active: bool
	is_verified: bool
	mfa_enabled: bool
	security_level: str
	created_at: datetime
	last_login: Optional[datetime] = None


# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> SecurityContext:
	"""Get current authenticated user"""
	# In a real implementation, you would validate the JWT token here
	# For now, we'll use a simple approach
	security_manager = await get_security_manager()

	# This is a placeholder - in production, you'd decode and validate the JWT
	# and extract user information from the token
	raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="JWT token validation not implemented")


# Authentication endpoints
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, request: Request):
	"""Register a new user"""
	try:
		security_manager = await get_security_manager()

		# Create user
		user = await security_manager.create_user(user_data)
		if not user:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create user")

		# Log registration event
		logger.info(f"User registered: {user.username}")

		return UserResponse(
			id=user.id,
			username=user.username,
			email=user.email,
			is_active=user.is_active,
			is_verified=user.is_verified,
			mfa_enabled=user.mfa_enabled,
			security_level=user.security_level,
			created_at=user.created_at,
			last_login=user.last_login,
		)
	except ValueError as e:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
	except Exception as e:
		logger.error(f"Registration error: {e}")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/login", response_model=AuthResponse)
async def login(login_data: LoginRequest, request: Request):
	"""Authenticate user and return access token"""
	try:
		security_manager = await get_security_manager()

		# Get client IP and user agent
		client_ip = request.client.host
		user_agent = request.headers.get("user-agent")

		# Authenticate user
		security_context = await security_manager.authenticate_user(
			username=login_data.username, password=login_data.password, mfa_code=login_data.mfa_code, ip_address=client_ip, user_agent=user_agent
		)

		if not security_context:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials or MFA required")

		# In a real implementation, you would generate a JWT token here
		# For now, we'll return a placeholder
		access_token = f"placeholder_token_{security_context.session_id}"

		return AuthResponse(
			access_token=access_token,
			expires_in=3600,  # 1 hour
			user={
				"id": security_context.user_id,
				"username": security_context.username,
				"security_level": security_context.security_level.value,
				"mfa_verified": security_context.mfa_verified,
			},
			permissions=security_context.permissions,
			roles=security_context.roles,
		)
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Login error: {e}")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/logout")
async def logout(request: Request, current_user: SecurityContext = Depends(get_current_user)):
	"""Logout user and invalidate token"""
	try:
		# In a real implementation, you would invalidate the JWT token
		# by adding it to a blacklist or updating its status
		logger.info(f"User logged out: {current_user.username}")

		return {"message": "Successfully logged out"}
	except Exception as e:
		logger.error(f"Logout error: {e}")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# MFA endpoints
@router.post("/mfa/enable", response_model=MFAEnableResponse)
async def enable_mfa(mfa_data: MFAEnableRequest, request: Request, current_user: SecurityContext = Depends(get_current_user)):
	"""Enable MFA for user"""
	try:
		security_manager = await get_security_manager()

		if mfa_data.method == AuthenticationMethod.TOTP:
			# Generate TOTP secret and QR code
			secret = security_manager.mfa_manager.generate_totp_secret(current_user.username)
			qr_code = security_manager.mfa_manager.generate_totp_qr_code(current_user.username, secret)
			backup_codes = security_manager.mfa_manager.generate_backup_codes()

			# Update user in database
			db_manager = get_database_manager()
			async with db_manager.get_session() as session:
				from ..core.security import User

				await session.execute(User.__table__.update().where(User.id == current_user.user_id).values(mfa_enabled=True, mfa_secret=secret))
				await session.commit()

			return MFAEnableResponse(secret=secret, qr_code=qr_code, backup_codes=backup_codes)
		else:
			raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"MFA method {mfa_data.method} not supported")
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"MFA enable error: {e}")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/mfa/verify")
async def verify_mfa(mfa_data: MFAVerifyRequest, request: Request, current_user: SecurityContext = Depends(get_current_user)):
	"""Verify MFA code"""
	try:
		security_manager = await get_security_manager()

		# Get user's MFA secret
		db_manager = get_database_manager()
		async with db_manager.get_session() as session:
			from ..core.security import User

			result = await session.execute(User.__table__.select().where(User.id == current_user.user_id))
			user_row = result.fetchone()

			if not user_row or not user_row.mfa_secret:
				raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="MFA not enabled for user")

			# Verify MFA code
			if security_manager.mfa_manager.verify_totp_code(user_row.mfa_secret, mfa_data.code):
				return {"message": "MFA verification successful"}
			else:
				raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code")
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"MFA verify error: {e}")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/mfa/disable")
async def disable_mfa(request: Request, current_user: SecurityContext = Depends(get_current_user)):
	"""Disable MFA for user"""
	try:
		db_manager = get_database_manager()
		async with db_manager.get_session() as session:
			from ..core.security import User

			await session.execute(User.__table__.update().where(User.id == current_user.user_id).values(mfa_enabled=False, mfa_secret=None))
			await session.commit()

		logger.info(f"MFA disabled for user: {current_user.username}")
		return {"message": "MFA disabled successfully"}
	except Exception as e:
		logger.error(f"MFA disable error: {e}")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


# User management endpoints
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: SecurityContext = Depends(get_current_user)):
	"""Get current user information"""
	try:
		db_manager = get_database_manager()
		async with db_manager.get_session() as session:
			from ..core.security import User

			result = await session.execute(User.__table__.select().where(User.id == current_user.user_id))
			user_row = result.fetchone()

			if not user_row:
				raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

			return UserResponse(
				id=user_row.id,
				username=user_row.username,
				email=user_row.email,
				is_active=user_row.is_active,
				is_verified=user_row.is_verified,
				mfa_enabled=user_row.mfa_enabled,
				security_level=user_row.security_level,
				created_at=user_row.created_at,
				last_login=user_row.last_login,
			)
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Get user info error: {e}")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.get("/permissions")
async def get_user_permissions(current_user: SecurityContext = Depends(get_current_user)):
	"""Get user permissions"""
	return {"permissions": current_user.permissions, "roles": current_user.roles, "security_level": current_user.security_level.value}


# Password management endpoints
@router.post("/password/check-strength")
async def check_password_strength(password: str):
	"""Check password strength"""
	try:
		security_manager = await get_security_manager()
		strength_check = security_manager.password_manager.check_password_strength(password)
		return strength_check
	except Exception as e:
		logger.error(f"Password strength check error: {e}")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")


@router.post("/password/generate")
async def generate_secure_password(length: int = 16):
	"""Generate a secure password"""
	try:
		security_manager = await get_security_manager()
		password = security_manager.password_manager.generate_secure_password(length)
		return {"password": password}
	except Exception as e:
		logger.error(f"Password generation error: {e}")
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
