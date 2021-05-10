from flask import session, request
import pytest

from types import SimpleNamespace

from flask_app.forms import RegistrationForm, UpdateUsernameForm
from flask_app.models import User


def test_register(client, auth):
    """ Test that registration page opens up """
    resp = client.get("/register")
    assert resp.status_code == 200

    response = auth.register()

    assert response.status_code == 200
    user = User.objects(username="test").first()

    assert user is not None


@pytest.mark.parametrize(
    ("username", "email", "password", "confirm", "message"),
    (
        ("test", "test@email.com", "test", "test", b"Username is taken"),
        ("p" * 41, "test@email.com", "test", "test", b"Field must be between 1 and 40"),
        ("username", "test", "test", "test", b"Invalid email address."),
        ("username", "test@email.com", "test", "test2", b"Field must be equal to"),
    ),
)
def test_register_validate_input(auth, username, email, password, confirm, message):
    if message == b"Username is taken":
        auth.register()

    response = auth.register(username, email, password, confirm)

    assert message in response.data


def test_login(client, auth):
    """ Test that login page opens up """
    resp = client.get("/login")
    assert resp.status_code == 200

    auth.register()
    response = auth.login()

    with client:
        client.get("/")
        assert session["_user_id"] == "test"


@pytest.mark.parametrize(("username", "password", "message"), 
(("usrnm", "", "This field is required"), 
("", "psswrd", "This field is required"),
("test", "wrongpsswrd", "Login failed. Check your username and/or password"),
("wrongusrn", "test", "Login failed. Check your username and/or password"))
)
def test_login_input_validation(auth, username, password, message):

    if username == "" or password == "":
        login_resp = auth.login(username, password)
        assert login_resp.status_code == 200
        assert str.encode(message) in login_resp.data

    else:
        # Register and login
        register_resp = auth.register()
        assert register_resp.status_code == 200

        login_resp = auth.login(username, password)
        assert str.encode(message) in login_resp.data






def test_logout(client, auth):
    resp = client.get("/login")
    assert resp.status_code == 200

    # Register and login
    register_resp = auth.register()
    assert register_resp.status_code == 200

    login_resp = auth.login()
    assert login_resp.status_code == 200

    with client:
        logout_resp = auth.logout()
        assert logout_resp.status_code == 302




def test_change_username(client, auth):
    resp = client.get("/login")
    assert resp.status_code == 200

    # Register and login
    register_resp = auth.register()
    assert register_resp.status_code == 200

    login_resp = auth.login()
    assert login_resp.status_code == 200

    with client:
        resp = client.get("/account")
        assert resp.status_code == 200

        update_username = SimpleNamespace(username="newusrnm", submit="Update Username")
        form = UpdateUsernameForm(formdata=None, obj=update_username)
        response = client.post("/account", data=form.data, follow_redirects=True)
        assert response.status_code == 200


    new_login_resp = auth.login(username="newusrnm")
    assert new_login_resp.status_code == 200
    with client:
        resp = client.get("/account")
        assert resp.status_code == 200
        assert str.encode("newusrnm") in resp.data

    # Check if username is saved in database
    in_db = False
    for u in User.objects().all():
        if u.username == "newusrnm":
            in_db = True
        
    assert in_db





def test_change_username_taken(client, auth):
    resp = client.get("/login")
    assert resp.status_code == 200

    # Register and login
    register_resp = auth.register()
    assert register_resp.status_code == 200

    login_resp = auth.login()
    assert login_resp.status_code == 200

    
    with client:
        logout_resp = auth.logout()
        assert logout_resp.status_code == 302

    
    # Register and login
    register_resp = auth.register(username="dffrntusrnm", email="dffrntusrnm@dffrntusrnm.com", passwrd="test", confirm="test")
    assert register_resp.status_code == 200

    login_resp = auth.login(username="dffrntusrnm", password="test")
    assert login_resp.status_code == 200

    with client:
        resp = client.get("/account")

        update_username = SimpleNamespace(username="test", submit="Update Username")
        form = UpdateUsernameForm(formdata=None, obj=update_username)
        response = client.post("/account", data=form.data, follow_redirects=True)
        message = "That username is already taken"
        assert response.status_code == 200
        assert str.encode(message) in response.data
        




@pytest.mark.parametrize(
    ("new_username", "message"), 
    (
        ("", "This field is required."), (('a' * 50), "Field must be between 1 and 40 characters long.")
    )
)
def test_change_username_input_validation(client, auth, new_username, message):
    resp = client.get("/login")
    assert resp.status_code == 200

    # Register and login
    register_resp = auth.register()
    assert register_resp.status_code == 200

    login_resp = auth.login()
    assert login_resp.status_code == 200

    with client:
        resp = client.get("/account")
        assert resp.status_code == 200

        update_username = SimpleNamespace(username=new_username, submit="Update Username")
        form = UpdateUsernameForm(formdata=None, obj=update_username)
        response = client.post("/account", data=form.data, follow_redirects=True)
        assert response.status_code == 200
        assert str.encode(message) in response.data
    
