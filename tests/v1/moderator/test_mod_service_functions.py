import datetime as dt
from api.v1.services.moderator import ModeratorService
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from api.v1.models.moderator import Moderator
from api.v1.services.moderator import mod_service
from unittest.mock import Mock
import jwt
from api.v1.services.moderator import settings
from fastapi.security import HTTPAuthorizationCredentials

import pytest

class TestModeratorService:

    # Creating a new moderator with valid data
    def test_create_moderator_with_valid_data(self, mocker):
        db = mocker.Mock()
        schema = mocker.Mock()
        schema.password = "password123"
        schema.model_dump.return_value = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "email": "john.doe@example.com",
            "password": "password123",
            "country_preferences": []
        }
        mocker.patch("api.v1.services.country.CountryService.fetch_countries", return_value=[])
        result = mod_service.create(db, schema)
        assert result.first_name == "John"
        assert result.email == "john.doe@example.com"

    # Fetching a moderator by their ID
    def test_fetch_moderator_by_id(self, mocker):
        db = mocker.Mock()
        mod = mocker.Mock(id='some-id')
        db.get.return_value = mod
        
        result = mod_service.fetch(db, "some-id")
        assert result == mod

    # Fetching a moderator by their email
    def test_fetch_moderator_by_email(self, mocker):
        db = mocker.Mock()
        mod = mocker.Mock(email="john.doe@example.com")
        db.query().filter().first.return_value = mod
        
        result = mod_service.fetch_by_email(db, "john.doe@example.com")
        assert result == mod

    # Updating a moderator's details with valid data and valid permission
    def test_update_moderator_with_valid_data(self, mocker):
        db = mocker.Mock()
        current_mod = mocker.Mock(id='some-id')
        mod = mocker.Mock(first_name='Gina')

        schema = mocker.Mock()
        schema.model_dump.return_value = {"first_name": "Jane"}
        
        db.get.return_value = mod
        result = mod_service.update(db, current_mod, schema, "some-id")
        
        assert result.first_name == "Jane"
        assert result == mod

    # Updating a moderator's details with valid data and valid permission
    def test_update_moderator_not_permitted(self, mocker):
        db = mocker.Mock()
        current_mod = mocker.Mock(id='wrong-id')
        mod = mocker.Mock(first_name='Gina')

        schema = mocker.Mock()
        schema.model_dump.return_value = {"first_name": "Jane"}
        
        db.get.return_value = mod

        with pytest.raises(HTTPException) as exc:
            mod_service.update(db, current_mod, schema, "some-id")
            assert exc.value.status_code == 403
            assert exc.value.detail == 'You do not have permission to access this resource'


    # Deactivating or activating a moderator with valid permissions
    def test_deactivate_or_activate_moderator_with_valid_permissions(self, mocker):
        db = mocker.Mock()
        current_mod_admin = mocker.Mock(is_admin=True)
        mod = mocker.Mock(is_active=True)
        db.get.return_value = mod

        result = mod_service.deactivateOrActivate(db, "some-id", current_mod_admin, False)
        assert result.is_active is False
        assert result is mod


        current_mod = mocker.Mock(id='some-id')
        db.get.return_value = mod

        result = mod_service.deactivateOrActivate(db, "some-id", current_mod, True)
        assert result.is_active is True
        assert result is mod


    
    # # Deactivating or activating a moderator with valid permissions
    def test_deactivate_or_activate_moderator_with_invalid_permissions(self, mocker):
        db = mocker.Mock()

        mod = mocker.Mock(is_active=False)
        current_mod = mocker.Mock(id='invalid-id', is_admin=False)
        db.get.return_value = mod

        with pytest.raises(HTTPException) as exc:
            mod_service.deactivateOrActivate(db, "some-id", current_mod, True)
            assert exc.value.status_code == 403
            assert exc.value.detail == 'You do not have permission to access this resource'


    # Authenticating a moderator with correct credentials
    def test_authenticate_moderator_with_correct_credentials(self, mocker):
        
        pwd = "hashed_password"
        h_pwd = mod_service.hash_password(pwd)
        
        db = mocker.Mock()
        mod = mocker.Mock(password=h_pwd)
        db.query().filter().first.return_value = mod
        

        result = mod_service.authenticate_mod(db, "john.doe@example.com", pwd)
        assert result == mod

    # Authenticating a moderator with incorrect credentials
    def test_authenticate_moderator_with_incorrect_credentials(self, mocker):
        
        pwd = "hashed_password"
        h_pwd = mod_service.hash_password("hash")
        
        db = mocker.Mock()
        mod = mocker.Mock(password=h_pwd)
        db.query().filter().first.return_value = mod
        

        # mocker.patch("api.v1.services.moderator.pwd_context.verify", return_value=True)
        with pytest.raises(HTTPException) as exc:
            mod_service.authenticate_mod(db, "john.doe@example.com", pwd)
            
            assert exc.value.status_code == 400
            assert exc.value.detail == 'Invalid user credentials'

    # Authenticating a deactivated moderator with correct credentials
    def test_authenticate_deactivated_moderator(self, mocker):
        
        pwd = "hashed_password"
        h_pwd = mod_service.hash_password(pwd)
        
        db = mocker.Mock()
        mod = mocker.Mock(password=h_pwd, is_active=False)
        db.query().filter().first.return_value = mod
        

        with pytest.raises(HTTPException) as exc:
            mod_service.authenticate_mod(db, "john.doe@example.com", h_pwd)
            
            assert exc.value.status_code == 401
            assert exc.value.detail == 'Deactivated account'


    # Creating a moderator with an existing email or username
    def test_create_moderator_with_existing_email_or_username(self, mocker):
        db = mocker.Mock()
        db_store = [mocker.Mock(email='john.doe@example.com')]
        schema = mocker.Mock()
        schema.password = "password123"
        schema.model_dump.return_value = {
            "first_name": "John",
            "last_name": "Doe",
            "username": "johndoe",
            "email": "john.doe@example.com",
            "password": "password123",
            "country_preferences": []
        }
        mocker.patch("api.v1.services.country.CountryService.fetch_countries", return_value=[])
        
        def db_add_mocker(mod_obj):
            if list(filter(lambda x: x.email == mod_obj.email, db_store)):
                raise IntegrityError(None, None, None)
        
        db.add = db_add_mocker
        with pytest.raises(HTTPException) as excinfo:
            mod_service.create(db, schema)
            assert excinfo.value.status_code == 400

    # Deleting a moderator
    def test_delete_moderator_by_admin(self, mocker):
        db = mocker.Mock()
        current_mod = mocker.Mock(is_admin=True)
        db_store = [mocker.Mock(email='john.doe@example.com')]
        
        
        def db_delete_mocker(mod_obj):
            if obj := list(filter(lambda x: x.email == mod_obj.email, db_store)):
                db_store.remove(obj[0])
                
        
        db.delete = db_delete_mocker
        result = mod_service.delete(db, 'some-id', current_mod)
        assert result == True


    # Deleting a moderator by regular moderator
    def test_delete_moderator_by_non_admin(self, mocker):
        db = mocker.Mock()
        current_mod = mocker.Mock(is_admin=False)

        with pytest.raises(HTTPException) as exc:
            mod_service.delete(db, 'some-id', current_mod)
            assert exc.value == 403
            assert exc.value.detail == 'You do not have permission to access this resource'



    # Fetching a moderator with a non-existent ID
    def test_fetch_moderator_with_non_existent_id(self, mocker):
        db = mocker.Mock()
        db.get.return_value = None
        
        result = mod_service.fetch(db, "non-existent-id")
        assert result is None



    # # Changing a moderator's password with incorrect old password
    def test_change_password_with_incorrect_old_password(self, mocker):
        db = mocker.Mock()
        user = mocker.Mock(password=mod_service.hash_password("hashed_password"))
        
        with pytest.raises(HTTPException) as excinfo:
            mod_service.change_password("wrongpassword", "newpassword", "newpassword", user, db)
            assert excinfo.value.status_code == 400
            assert excinfo.value.detail == 'Incorrect old password.'

    # Changing a moderator's password with correct old password and matching new passwords
    def test_change_moderator_password_correct_old_and_matching_new(self, mocker):
        db = mocker.Mock()
        user = Moderator()
        user.password = mod_service.hash_password("old_password")
        old_password = "old_password"
        new_password = "new_password"
        confirm_new_password = "new_password"


        mod_service.change_password(old_password, new_password, confirm_new_password, user, db)

        assert mod_service.verify_password("new_password", user.password) is\
            True


    
    # Changing a moderator's password with non-matching new passwords
    def test_change_password_non_matching_new_passwords(self, mocker):
        # Arrange
        db = mocker.Mock()
        user = Moderator()
        user.password = mod_service.hash_password("old_password")
        old_password = "old_password"
        new_password = "new_password"
        confirm_new_password = "confirm_new_password"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            mod_service.change_password(old_password, new_password, confirm_new_password, user, db)
            
            assert exc_info.value.status_code == 400
            assert exc_info.value.detail == "New password and confirmation do not match."




    # Verifying access and refresh tokens
    def test_verify_access_token_valid(self, mocker):
        db = mocker.Mock()
        access_token = "valid_access_token"
        credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
        mod_id = "valid_mod_id"
        payload = {"mod_id": mod_id, "exp": "future_date", "type": "access"}
        
        mocker.patch("jwt.decode", return_value=payload)
        
        result = mod_service.verify_access_token(access_token, credentials_exception)
        assert result == mod_id

    # # Generating access and refresh tokens for a moderator
    def test_generate_access_refresh_tokens(self, mocker):
        # Arrange        
        mod_id = "12345"
        access_token_expiry = 30  # minutes
        refresh_token_expiry = 7  # days
        secret_key = "super_secret_key"
        algorithm = "HS256"

        mocker.patch.object(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", access_token_expiry)
        mocker.patch.object(settings, "JWT_REFRESH_EXPIRY", refresh_token_expiry)
        mocker.patch.object(settings, "SECRET_KEY", secret_key)
        mocker.patch.object(settings, "ALGORITHM", algorithm)
    
        mocker.patch.object(mod_service, 'verify_refresh_token', return_value=mod_id)
        mocker.patch.object(mod_service, 'create_access_token', return_value="new_access_token")
        mocker.patch.object(mod_service, 'create_refresh_token', return_value="new_refresh_token")
        

        # Act
        access_token, refresh_token = mod_service.refresh_access_token("current_refresh_token")
    
        # Assert
        assert access_token == "new_access_token"
        assert refresh_token == "new_refresh_token"

    # Fetching the current logged-in moderator with an invalid access token
    def test_fetch_current_mod_with_invalid_token(self, mocker):
        # Arrange
        db = mocker.Mock()
        # mocker.patch("api.v1.services.moderator.OAuth2PasswordBearer", return_value=Mock(tokenUrl="/api/v1/auth/login"))
        # mocker.patch("api.v1.services.moderator.ModeratorService.verify_access_token", side_effect=HTTPException(status_code=401, detail="Access token expired"))

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            creds = HTTPAuthorizationCredentials(scheme='bearer', credentials="invalid_token")
            mod_service.get_current_mod(credentials=creds, db=db)
            assert exc.value.detail == 'Could not validate credentials'

    # # Fetching the current logged-in moderator using a valid access token
    def test_fetch_current_logged_in_moderator(self, mocker):
        # Arrange
        db = mocker.Mock()

        token = 'valid-token'
        mod = mocker.Mock(first_name="John", last_name="Doe")

        # Mocking the verify_access_token method to return a moderator id
        mocker.patch.object(mod_service, "verify_access_token", return_value="valid_mod_id")

        
        db.get.return_value = mod

        # Act
        creds = HTTPAuthorizationCredentials(scheme='bearer', credentials=token)
        result = mod_service.get_current_mod(credentials=creds, db=db)

        # Assert
        assert result.first_name == "John"
        assert result.last_name == "Doe"


    # Creating access token
    def test_create_access_token(self):
        token = mod_service.create_access_token('valid-id')

        payload = jwt.decode(token, settings.SECRET_KEY, [settings.ALGORITHM])
        
        assert payload['mod_id'] == "valid-id"
        assert payload['type'] == "access"


    # Verify access token
    def test_verify_access_token(self):
        
        expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        data = {"mod_id": 'valid-id', "exp": expires, "type": "access"}
        token = jwt.encode(data, settings.SECRET_KEY, settings.ALGORITHM)

        mod_id = mod_service.verify_access_token(token, None)

        assert mod_id == "valid-id"


    # Verifying an invalid refresh token
    def test_verify_invalid_refresh_token(self):
        # Arrange
        invalid_refresh_token = "invalid_token"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            mod_service.verify_refresh_token(invalid_refresh_token, HTTPException(status_code=401, detail="Could not validate refresh token"))
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == 'Could not validate refresh token'

    # Verifying an expired access token
    def test_verify_expired_access_token(self, mocker):
        # Arrange
        expires = dt.datetime.now(dt.timezone.utc) - dt.timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        data = {"mod_id": 'valid-id', "exp": expires, "type": "access"}
        access_token = jwt.encode(data, settings.SECRET_KEY, settings.ALGORITHM)


        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            mod_service.verify_access_token(access_token, None)
    
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Access token expired"
