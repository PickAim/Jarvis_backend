import sys

ACCESS_TOKEN_USAGE_URL_PART = "/access"
UPDATE_TOKEN_USAGE_URL_PART = "/update"

ACCESS_TOKEN_NAME = "access_token"
UPDATE_TOKEN_NAME = "update_token"
IMPRINT_TOKEN_NAME = "imprint_token"

IS_DEBUG = False

__trace_getter = getattr(sys, 'gettrace', None)
if __trace_getter is not None and __trace_getter():
    IS_DEBUG = True
