import pytest

from types import SimpleNamespace
import random
import string

from flask_app.forms import SearchForm, MovieReviewForm
from flask_app.models import User, Review


def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200

    search = SimpleNamespace(search_query="guardians", submit="Search")
    form = SearchForm(formdata=None, obj=search)
    response = client.post("/", data=form.data, follow_redirects=True)

    assert b"Guardians of the Galaxy" in response.data


@pytest.mark.parametrize(
    "query, message", 
    (("", "This field is required."), 
    ("Th", "Too many results"), 
    ("zxcvzxcv", "Movie not found"), 
    ("asdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdfasdf", "Field must be between 1 and 100 characters long."))
)
def test_search_input_validation(client, query, message):
    
    resp = client.get("/")
    assert resp.status_code == 200

    search = SimpleNamespace(search_query=query, submit="Search")
    form = SearchForm(formdata=None, obj=search)
    response = client.post("/", data=form.data, follow_redirects=True)
    
    assert str.encode(message) in response.data






def test_movie_review(client, auth):
    guardians_id = "tt2015381"
    url = f"/movies/{guardians_id}"
    resp = client.get(url)

    assert resp.status_code == 200

    # Register and login
    register_resp = auth.register()
    assert register_resp.status_code == 200

    login_resp = auth.login()
    assert login_resp.status_code == 200

    # Submit random review
    with client:
        random_review = ''.join(random.choice(string.ascii_letters) for i in range(20))
        review = SimpleNamespace(text=random_review, submit="Enter Comment")
        form = MovieReviewForm(formdata=None, obj=review)
        response = client.post(url, data=form.data, follow_redirects=True)
        assert str.encode(random_review) in response.data
    
    # Review is saved in database
    in_db = False
    for r in Review.objects().all():
        if r.content == random_review:
            in_db = True
        
    assert in_db


    




@pytest.mark.parametrize(
    ("movie_id", "message"), 
    (
        ("", "404 - Page Not Found"),
        ("short", "Incorrect IMDb ID"),
        ("123456789", "Incorrect IMDb ID"),
        ("asdfasdfasdf", "Incorrect IMDb ID")
    )
)
def test_movie_review_redirects(client, movie_id, message):
    
    if movie_id == "":
        url = f"/movies/{movie_id}"
        resp = client.get(url)
        assert resp.status_code == 404
        assert str.encode(message) in resp.data

    else:
        url = f"/movies/{movie_id}"
        resp_redir_false = client.get(url, follow_redirects=False)
        assert resp_redir_false.status_code == 302

        resp_redir_true = client.get(url, follow_redirects=True)
        #assert resp.status_code == 202
        assert str.encode(message) in resp_redir_true.data


@pytest.mark.parametrize(
    ("comment", "message"), 
    (
        ("", "This field is required"),
        ("shrt", "Field must be between 5 and 500 characters long."),
        (('a' * 505), "Field must be between 5 and 500 characters long.") 
    )
)
def test_movie_review_input_validation(client, auth, comment, message):
    
    # Register and login
    register_resp = auth.register()
    assert register_resp.status_code == 200

    login_resp = auth.login()
    assert login_resp.status_code == 200

    # Submit random review
    with client:
        #random_review = ''.join(random.choice(string.ascii_letters) for i in range(20))
        review = SimpleNamespace(text=comment, submit="Enter Comment")
        form = MovieReviewForm(formdata=None, obj=review)
        response = client.post("/movies/tt2015381", data=form.data, follow_redirects=True)
        assert str.encode(message) in response.data