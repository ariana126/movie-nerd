from assertpy.assertpy import assert_that
from ddd import Identity
from pydm import ServiceContainer

from movie_nerd.domain import User
from movie_nerd.domain.service import UserRepository

service_container = ServiceContainer.get_instance()

def test_saved_user_will_be_returned():
    user = User(Identity.new(), 'dummy-name@example.com', 'dummy-password-hash', 'dummy-name', 'dummy-name')
    sut = service_container.get_service(UserRepository)
    sut.save(user)

    fetched_user = sut.find(user.id)

    assert_that(fetched_user).is_not_none()
    assert_that(fetched_user).is_equal_to(user)
    assert_that(fetched_user.first_name).is_equal_to(user.first_name)
    assert_that(fetched_user.last_name).is_equal_to(user.last_name)
    assert_that(fetched_user.email).is_equal_to(user.email)
    assert_that(fetched_user.password).is_equal_to(user.password)
