from typing import Optional, Annotated
import datetime as dt
from fastapi import status
from pydantic import EmailStr

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
)
import jwt
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

from api.db.database import get_db
from api.utils.settings import settings
from api.core.base.services import Service
from api.v1.models.moderator import Moderator
from api.v1.services.country import CountryService
from api.v1.schemas import moderator

bearer_scheme = HTTPBearer(auto_error=False)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class ModeratorService(Service):
    """Moderator service"""

    DUP_EXC = HTTPException(
        status_code=400,
        detail="Moderator with this email or username already exists",
    )

    FORBIDDEN_EXC = HTTPException(
        status_code=403,
        detail="You do not have permission to access this resource",
    )

    NOT_FOUND_EXC = HTTPException(
        status_code=404,
        detail="Moderator not found",
    )

    CREDENTIALS_EXC = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    def fetch_all(self, db: Session) -> list[Moderator]:
        """Fetches all moderators from the database

        Args:
            db (Session): Db session object

        Returns:
            list[Moderator]: A list of all Moderator objects on the database
        """
        all_moderators = db.query(Moderator).all()
        return all_moderators

    def fetch(self, db: Session, id: str):
        """Fetches a moderator by their id"""

        mod = db.get(Moderator, id)
        return mod

    def fetch_by_email(self, db: Session, email: EmailStr) -> Moderator | None:
        """Fetches a moderator by their email"""

        mod = db.query(Moderator).filter(Moderator.email == email).first()
        return mod

    def create(
        self,
        db: Session,
        schema: moderator.CreateModeratorSchema,
        is_admin: bool = False,
    ) -> Moderator:
        """Creates a new moderator


        Args:
            db (Session): Database session
            schema (moderator.CreateModeratorSchema): Pydantic Schema
            is_admin (bool, optional): Should mod be an admin. Defaults to False.

        Raises:
            DUP_EXC: If user account already exists

        Returns:
            Moderator: Return newly created moderator
        """

        # Hash password
        schema.password = self.hash_password(password=schema.password)

        try:
            schema_dump = schema.model_dump()
            countries_pref = schema_dump.pop("country_preferences", [])
            country_models_list = CountryService.fetch_countries(db, countries_pref)

            mod = Moderator(**schema_dump)
            mod.is_admin = is_admin
            mod.country_preferences = country_models_list

            db.add(mod)
            db.commit()
            db.refresh(mod)

        except IntegrityError as e:
            raise self.DUP_EXC
        return mod

    def update(
        self,
        db: Session,
        current_mod: Moderator,
        schema: moderator.UpdateModeratorSchema,
        id_target: str,
    ):
        """Update the moderator specified by id_target. Only an admin or
        the moderator should be allowed to make these changes

        Args:
            db (Session):
            current_mod (Moderator): Logged-in moderator as determined from access_token
            schema (moderator.UpdateModeratorSchema): Pydantic schema for updating model
            id_target (str): Target mod  idto be updated

        Raises:
            dup_exception: Raised if update violated unique constraint

        Returns:
            Moderator: updated moderator object
        """
        if id_target != current_mod.id:
            raise self.FORBIDDEN_EXC

        mod = self.fetch(db=db, id=id_target)

        if not mod:
            raise self.NOT_FOUND_EXC

        update_data = schema.model_dump(exclude_unset=True)
        countries_pref = update_data.pop("country_preferences", [])
        country_models = CountryService.fetch_countries(db, countries_pref)

        for key, value in update_data.items():
            setattr(mod, key, value)

        mod.country_preferences = country_models
        db.commit()
        db.refresh(mod)
        return mod

    def deactivateOrActivate(
        self,
        db: Session,
        id_target: str,
        current_mod: Moderator,
        is_active: bool = False,
    ) -> Moderator:
        """Function to deactivate or reactivate a mod.
        Only an admin or the target mod has permission to make changes.

        Args:
            db (Session):
            id_target (str): Id of the target moderator
            currrent_mod (Moderator): Moderator doing the deactivation

        Raises:
            self.FORBIDDEN_EXC: Raised if mod is not admin or target mod
            self.NOT_FOUND_EXC: Raised if mod id_target is invalid

        Returns:
            Moderator: _description_
        """

        if current_mod.is_admin is not True and id_target != current_mod.id:
            raise self.FORBIDDEN_EXC

        target_mod = self.fetch(db=db, id=id_target)

        if not target_mod:
            raise self.NOT_FOUND_EXC

        target_mod.is_active = is_active
        db.commit()
        db.refresh(target_mod)

        return target_mod

    def delete(self, db: Session, id_target: str, current_admin: Moderator) -> bool:
        """Function to delete a mod account. Only an admin has permission.

        Args:
            db (Session):
            id_target (str): Id of the target moderator
            currrent_admin (Moderator): Admin doing the deletion

        Raises:
            self.FORBIDDEN_EXC: Raised if mod is not admin or target mod
            self.NOT_FOUND_EXC: Raised if mod id_target is invalid

        Returns:
            Moderator: _description_
        """

        if current_admin.is_admin is not True:
            raise self.FORBIDDEN_EXC

        mod = self.fetch(db=db, id=id_target)

        if not mod:
            raise self.NOT_FOUND_EXC

        db.delete(mod)
        db.commit()

        return True

    def authenticate_mod(self, db: Session, email: EmailStr, password: str):
        """Function to authenticate a moderator"""

        mod: Moderator = self.fetch_by_email(db, email=email)

        if not mod:
            raise HTTPException(status_code=400, detail="Invalid user credentials")

        if not self.verify_password(password, mod.password):
            raise HTTPException(status_code=400, detail="Invalid user credentials")

        if mod.is_active is False:
            raise HTTPException(status_code=401, detail="Deactivated account")

        return mod

    def hash_password(self, password: str) -> str:
        """Function to hash a password"""

        hashed_password = pwd_context.hash(secret=password)
        return hashed_password

    def verify_password(self, password: str, hash: str) -> bool:
        """Function to verify a hashed password"""

        return pwd_context.verify(secret=password, hash=hash)

    def create_access_token(self, mod_id: str) -> str:
        """Function to create access token"""

        expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        data = {"mod_id": mod_id, "exp": expires, "type": "access"}
        encoded_jwt = jwt.encode(data, settings.SECRET_KEY, settings.ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, mod_id: str) -> str:
        """Function to create access token"""

        expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(
            days=settings.JWT_REFRESH_EXPIRY
        )
        data = {"mod_id": mod_id, "exp": expires, "type": "refresh"}
        encoded_jwt = jwt.encode(data, settings.SECRET_KEY, settings.ALGORITHM)
        return encoded_jwt

    def verify_access_token(
        self, access_token: str, credentials_exception: HTTPException
    ):
        """Funtcion to decode and verify access token"""

        try:
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            mod_id = payload.get("mod_id")
            token_type = payload.get("type")

            if mod_id is None:
                raise credentials_exception

            if token_type != "access":
                raise HTTPException(detail="Only access token allowed", status_code=401)

            return mod_id

        except jwt.exceptions.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Access token expired")
        except jwt.exceptions.InvalidTokenError:
            raise credentials_exception

    def verify_refresh_token(
        self, refresh_token: str, credentials_exception: HTTPException
    ):
        """Funtcion to decode and verify refresh token"""

        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            mod_id = payload.get("mod_id")
            token_type = payload.get("type")

            if mod_id is None:
                raise credentials_exception

            if token_type != "refresh":
                raise HTTPException(
                    detail="Only refresh token allowed", status_code=401
                )

            return mod_id

        except jwt.exceptions.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token expired")
        except jwt.exceptions.InvalidTokenError:
            raise credentials_exception

    def refresh_access_token(self, current_refresh_token: str | None):
        """Function to generate new access token and rotate refresh token"""

        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate refresh token",
        )

        if current_refresh_token is None:
            raise credentials_exception

        mod_id = self.verify_refresh_token(current_refresh_token, credentials_exception)

        access = self.create_access_token(mod_id=mod_id)
        refresh = self.create_refresh_token(mod_id=mod_id)

        return access, refresh

    def get_user_from_refresh_token(self, refresh_token: str, db: Session):
        """Returns the the mod embedded in the refresh token"""

        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate refresh token",
        )

        mod_id = self.verify_refresh_token(refresh_token, credentials_exception)
        mod = self.fetch(db, mod_id)
        if not mod:
            raise credentials_exception
        return mod

    def get_current_mod(
        self,
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
        db: Session = Depends(get_db),
    ) -> Moderator:
        """Function to get current logged in mod"""

        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        if credentials is None:
            raise credentials_exception

        mod_id = self.verify_access_token(
            credentials.credentials, credentials_exception
        )
        mod = self.fetch(db, mod_id)
        if not mod:
            raise credentials_exception
        return mod

    def get_current_mod_optional(
        self,
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
        db: Session = Depends(get_db),
    ) -> Optional[Moderator]:
        """Used to optionally check for a mod."""

        if credentials is None:
            return None

        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        mod_id = self.verify_access_token(
            credentials.credentials, credentials_exception
        )
        mod = self.fetch(db, mod_id)
        if not mod:
            raise credentials_exception
        return mod

    def change_password(
        self,
        old_password: str,
        new_password: str,
        confirm_new_password: str,
        user: Moderator,
        db: Session,
    ) -> bool:
        """Service function to change the user's password"""

        # If the user has a password, proceed with the normal password change process
        if not self.verify_password(old_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect old password.",
            )

        if new_password != confirm_new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password and confirmation do not match.",
            )

        user.password = self.hash_password(new_password)
        db.commit()

    def get_current_admin(
        self,
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
        db: Session = Depends(get_db),
    ):
        """Get the current super admin"""
        mod = self.get_current_mod(db=db, credentials=credentials)
        if mod.is_admin is not True:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this resource",
            )
        return mod

    def get_fullname(self, mod):
        return f"{mod.first_name} {mod.last_name}"


mod_service = ModeratorService()
