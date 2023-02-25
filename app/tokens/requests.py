from fastapi import APIRouter, Depends

from app.constants import UPDATE_TOKEN_USAGE_URL_PART
from app.handlers import session_controller
from app.tokens.util import update_token_correctness_depend, save_and_return_session_tokens

token_router = APIRouter()


@token_router.get(UPDATE_TOKEN_USAGE_URL_PART + '/update_all_tokens')
def update_tokens(update_token: str = Depends(update_token_correctness_depend)):
    new_access_token, new_update_token = session_controller.update_token(update_token)
    return save_and_return_session_tokens(new_access_token, new_update_token)
