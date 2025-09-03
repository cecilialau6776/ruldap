from coldfront.plugins.ldap_user_search.utils import LDAPUserSearch
from coldfront.core.utils.common import import_from_settings
from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth import get_user_model

import logging

logger = logging.getLogger(__name__)
UserModel = get_user_model()


class LDAPRemoteUserBackend(RemoteUserBackend):
    create_unknown_user = False

    def __init__(self):
        super().__init__()

    def authenticate(self, request, remote_user):
        if not remote_user:
            return None
        search_term = self.clean_username(remote_user)
        search_by = import_from_settings("RULDAP_SEARCH_BY", "username")
        search = LDAPUserSearch(search_term, search_by)
        search_results = search.search_a_user(search_term, search_by)
        self.user_dict = search_results
        self.CONFIGURE_USER = import_from_settings("RULDAP_CONFIGURE_USER", configure_user)
        if len(self.user_dict) == 0:
            # LDAP doesn't have this user
            return None
        else:
            self.create_unknown_user = True
        self.user_dict = self.user_dict[0]
        username = self.user_dict["username"]

        # Copy-pasted from https://github.com/django/django/blob/stable/3.2.x/django/contrib/auth/backends.py#L200C9-L211C66
        if self.create_unknown_user:
            user, created = UserModel._default_manager.get_or_create(**{
                UserModel.USERNAME_FIELD: username
            })
            if created:
                user = self.CONFIGURE_USER(self, request, user, created)
        else:
            try:
                user = UserModel._default_manager.get_by_natural_key(username)
            except UserModel.DoesNotExist:
                pass
        user = self.CONFIGURE_USER(self, request, user)
        return user

    def clean_username(self, username):
        return username
        # return username.split("@")[0]

def configure_user(self, request, user, created=False):
    ud = self.user_dict
    user.first_name = ud["first_name"]
    user.last_name = ud["last_name"]
    user.email = ud["email"]
    user.save()
    return user
