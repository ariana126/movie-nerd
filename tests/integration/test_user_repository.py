from assertpy.assertpy import assert_that
from ddd import Identity
from pydm import ServiceContainer

from movie_nerd.domain import User
from movie_nerd.domain.service import UserRepository
from movie_nerd.infrastructure.bootstrap.app import App

App.boot()
service_container = ServiceContainer.get_instance()

def test_saved_user_will_be_returned():
    user = User(Identity.new(), 'dummy-name', 'dummy-name')
    sut = service_container.get_service(UserRepository)
    sut.save(user)

    fetched_user = sut.find(user.id)

    assert_that(fetched_user).is_not_none()
    assert_that(fetched_user).is_equal_to(user)
