import pytest

from src.admin import admin_user_remove_v1
from src.auth import auth_register_v2, auth_login_v2, auth_logout_v1
from src.channel import channel_messages_v2
from src.channels import channels_listall_v2
from src.user import user_profile_v2
from src.other import clear_v2
from src.error import InputError, AccessError

@pytest.fixture
def reg_user():  
    def _register_user(num):
        return auth_register_v2(f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _register_user

@pytest.fixture
def user_details():
    def _user_details(num):
        return (f"example{num}@email.com", f"Password{num}", f"firstname{num}", f"lastname{num}")
    return _user_details

def test_successful_logout_after_register(reg_user): # Ensure that logout works at most basic level
    clear_v2()
    user_token = reg_user(0)['token']
    assert auth_logout_v1(user_token)['is_success']

def test_logout_then_channels_listall(reg_user): # Ensure that token becomes invalid after logout
    clear_v2()
    user_token = reg_user(0)['token']
    assert auth_logout_v1(user_token)['is_success']
    with pytest.raises(AccessError):
        channels_listall_v2(user_token)

def test_successful_logout_after_login(reg_user, user_details): # Test that token generated by login can be logged out
    clear_v2()
    user_token = reg_user(0)['token']
    email, pword, *_ = user_details(0)
    auth_logout_v1(user_token)
    user_token = auth_login_v2(email, pword)['token']
    assert auth_logout_v1(user_token)

def test_logout_with_multiple_users(reg_user, user_details): # Test that token generated by login can be logged out
    clear_v2()
    user_token = reg_user(0)['token']
    user_2 = reg_user(1)
    auth_logout_v1(user_token)
    user_profile_v2(user_2['token'], user_2['auth_user_id']) # Verify that the second user's token is still valid

def test_logout_after_already_logged_out(reg_user): # Token should be made invalid by first logout, raise AccessError
    clear_v2()
    user_token = reg_user(0)['token']
    auth_logout_v1(user_token)
    with pytest.raises(AccessError):
        auth_logout_v1(user_token)

def test_invalid_token(reg_user): # Invalid token should raise AccessError
    clear_v2()
    reg_user(0)
    with pytest.raises(AccessError):
        auth_logout_v1("invalid token")