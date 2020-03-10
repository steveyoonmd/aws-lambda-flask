from enum import IntEnum


class Error(IntEnum):
    NONE = 0
    UNKNOWN = 1

    # 1000
    ACCESS_NOT_ALLOWED_IP_ADDR = 1001

    # 1100
    USER_LOGIN_REQUIRED = 1101
    USER_LOGIN_FAILED = 1102

    # 1200
    CSRF_TOKEN_INVALID = 1200
