from django.contrib import auth
from django.contrib.auth.middleware import RemoteUserMiddleware
from coldfront.core.utils.common import import_from_settings


class CustomHeaderMiddleware(RemoteUserMiddleware):
    header = import_from_settings("RULDAP_CUSTOM_HEADER", "REMOTE_USER")

    # Copy-pasted from https://github.com/django/django/blob/848fe70f3ee6dc151831251076dc0a4a9db5a0ec/django/contrib/auth/middleware.py#L46
    def process_request(self, request):
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The Django remote user auth middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the RemoteUserMiddleware class.")
        try:
            username = request.META[self.header]
        except KeyError:
            # If specified header doesn't exist then remove any existing
            # authenticated remote-user, or return (leaving request.user set to
            # AnonymousUser by the AuthenticationMiddleware).
            if self.force_logout_if_no_header and request.user.is_authenticated:
                self._remove_invalid_user(request)
            return
        # If the user is already authenticated and that user is the user we are
        # getting passed in the headers, then the correct user is already
        # persisted in the session and we don't need to continue.
        if request.user.is_authenticated:
            # changed get_username() to email; since that's what we're using
            expect_email = import_from_settings("RULDAP_EXPECT_EMAIL", False)
            check_query = request.user.email if expect_email else request.user.username
            if check_query == self.clean_username(username, request):
                return
            else:
                # An authenticated user is associated with the request, but
                # it does not match the authorized user in the header.
                self._remove_invalid_user(request)

        # We are seeing this user for the first time in this session, attempt
        # to authenticate the user.
        user = auth.authenticate(request, remote_user=username)
        if user:
            # User is valid.  Set request.user and persist user in the session
            # by logging the user in.
            request.user = user
            auth.login(request, user)
