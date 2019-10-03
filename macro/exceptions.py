''' Exception classes for macro module '''


class ConsentRequiredException(Exception):
    ''' Raised when consent is required '''


class AuthenticationFailureException(Exception):
    ''' Raised when authentication is failed '''


class AccountBannedException(Exception):
    ''' Raised when account ban is detected '''


class RateLimitedException(Exception):
    ''' Raised when the login rate is limited '''


class BadUsernameException(Exception):
    ''' Raised when summoner name is not available '''
