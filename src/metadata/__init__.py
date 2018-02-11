from sqlalchemy.ext.declarative import declarative_base

base = None


# TODO Use Django models instead
def get_dec_base():
    global base  # pylint:disable=W0603
    if base is None:
        # This is the only time we instantiate a declarative base instance!
        base = declarative_base()
    return base


class ResolutionException(Exception):
    def __init__(self, *args):
        if args:
            message = str.format(args[0], *(args[1:]))
            super().__init__(message)
        else:
            super().__init__()


class RDAPResolutionException(ResolutionException):
    def __init__(self, msg, *msg_args, whois_host=None):
        super().__init__(msg, *msg_args)
        self.whois_host = whois_host


class RDAPRedirectException(ResolutionException):
    def __init__(self, msg, *msg_args, provisional=None, redir_url=None):
        super().__init__(msg, *msg_args)
        self.provisional = provisional
        self.redir_url = redir_url


class RDAPRedirectionDetected(ResolutionException):
    def __init__(self, redir_url=None, redir_json=None):
        super().__init__("HTTP Redirection detected while fetching RDAP JSON")
        self.redir_url = redir_url
        self.redir_json = redir_json


class RateLimitationException(ResolutionException):
    pass


class DataException(Exception):
    pass
