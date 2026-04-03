import os

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.schemas import (
    ForgotPasswordDTO,
    LoginDTO,
    MessageResponse,
    RegisterDTO,
    ResetPasswordDTO,
    UserProfileResponse,
)
from app.auth.service import AuthService
from app.config import FRONTEND_URL
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

_oauth_states: set[str] = set()

_401_auth = {
    "description": "Неверные учётные данные или токен",
    "content": {"application/json": {"example": {"detail": "Неверные учётные данные"}}},
}
_409_auth = {
    "description": "Конфликт",
    "content": {
        "application/json": {
            "example": {"detail": "Пользователь с таким email уже существует"}
        }
    },
}


def _set_cookies(response: Response, access: str, refresh: str):
    response.set_cookie("access_token", access, httponly=True, max_age=900)
    response.set_cookie("refresh_token", refresh, httponly=True, max_age=604800)


def _clear_cookies(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")


def get_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post(
    "/register",
    response_model=MessageResponse,
    status_code=201,
    summary="Регистрация нового пользователя",
    description="Создаёт нового пользователя с указанными username, email и паролем",
    responses={201: {"description": "Регистрация успешна"}, 409: _409_auth},
)
def register(data: RegisterDTO, svc: AuthService = Depends(get_service)):
    svc.register(data.username, data.email, data.password)
    return {"message": "Регистрация успешна"}


@router.post(
    "/login",
    response_model=MessageResponse,
    summary="Авторизация пользователя (Login)",
    description="Проверяет email и пароль. В случае успеха устанавливает HttpOnly cookies с access и refresh токенами.",
    responses={200: {"description": "Успешный вход"}, 401: _401_auth},
)
def login(data: LoginDTO, response: Response, svc: AuthService = Depends(get_service)):
    user, access, refresh = svc.login(data.email, data.password)
    _set_cookies(response, access, refresh)
    return {"message": "Вход выполнен"}


@router.post(
    "/refresh",
    response_model=MessageResponse,
    summary="Обновление токенов доступа",
    description="Использует refresh токен из cookies для получения новой пары токенов",
    responses={200: {"description": "Токены успешно обновлены"}, 401: _401_auth},
)
def refresh(
    response: Response,
    refresh_token: str = Cookie(None),
    svc: AuthService = Depends(get_service),
):
    if not refresh_token:
        raise HTTPException(401, "Refresh token отсутствует")
    user, access, new_refresh = svc.refresh(refresh_token)
    _set_cookies(response, access, new_refresh)
    return {"message": "Токены обновлены"}


@router.get(
    "/whoami",
    response_model=UserProfileResponse,
    summary="Получение информации о текущем пользователе",
    description="Возвращает профиль авторизованного пользователя",
    responses={200: {"description": "Профиль пользователя"}, 401: _401_auth},
)
def whoami(
    current: dict = Depends(get_current_user), svc: AuthService = Depends(get_service)
):
    user = svc.get_profile(current["user_id"])
    return UserProfileResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        os=user.os,
        totaltime=user.totaltime,
        created_at=str(user.created_at),
        updated_at=str(user.updated_at),
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Выход из текущей сессии",
    description="Завершает текущую сессию пользователя и удаляет токены из cookies",
    responses={200: {"description": "Выход выполнен успешно"}, 401: _401_auth},
)
def logout(
    response: Response,
    current: dict = Depends(get_current_user),
    svc: AuthService = Depends(get_service),
):
    svc.logout(current["access_token"])
    _clear_cookies(response)
    return {"message": "Выход выполнен"}


@router.post(
    "/logout-all",
    response_model=MessageResponse,
    summary="Завершение всех сессий пользователя",
    description="Завершает все активные сессии пользователя и удаляет текущие токены из cookies",
    responses={200: {"description": "Все сессии завершены"}, 401: _401_auth},
)
def logout_all(
    response: Response,
    current: dict = Depends(get_current_user),
    svc: AuthService = Depends(get_service),
):
    svc.logout_all(current["user_id"])
    _clear_cookies(response)
    return {"message": "Все сессии завершены"}


@router.get(
    "/oauth/{provider}",
    summary="Инициация OAuth аутентификации",
    description="Перенаправляет пользователя на страницу аутентификации указанного провайдера",
    responses={
        302: {"description": "Перенаправление на OAuth провайдера"},
        400: {"description": "Провайдер не поддерживается"},
    },
)
def oauth_init(provider: str):
    if provider != "yandex":
        raise HTTPException(400, "Провайдер не поддерживается")
    state = os.urandom(16).hex()
    _oauth_states.add(state)
    url = AuthService.get_yandex_auth_url(state)
    return RedirectResponse(url, status_code=302)


@router.get(
    "/oauth/{provider}/callback",
    summary="OAuth callback",
    description="Обрабатывает callback от OAuth провайдера, выполняет аутентификацию и устанавливает токены",
    responses={
        302: {"description": "Перенаправление на фронтенд с установленными токенами"},
        400: {"description": "Невалидный state или неподдерживаемый провайдер"},
    },
)
def oauth_callback(
    provider: str,
    code: str,
    state: str,
    response: Response,
    svc: AuthService = Depends(get_service),
):
    if provider != "yandex":
        raise HTTPException(400, "Провайдер не поддерживается")
    if state not in _oauth_states:
        raise HTTPException(400, "Невалидный state")
    _oauth_states.discard(state)

    user, access, refresh = svc.handle_yandex_callback(code)
    redirect = RedirectResponse(FRONTEND_URL, status_code=302)
    _set_cookies(redirect, access, refresh)
    return redirect


@router.post(
    "/forgot-password",
    summary="Запрос на восстановление пароля",
    description="Отправляет инструкции по восстановлению пароля на указанный email",
    responses={
        200: {"description": "Инструкции отправлены (или email не существует)"},
        404: {"description": "Пользователь с таким email не найден"},
    },
)
def forgot_password(data: ForgotPasswordDTO, svc: AuthService = Depends(get_service)):
    token = svc.forgot_password(data.email)
    return {
        "message": "Если email существует, инструкции отправлены",
        "reset_token": token,
    }


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Сброс пароля",
    description="Устанавливает новый пароль с использованием токена сброса",
    responses={
        200: {"description": "Пароль успешно изменён"},
        400: {"description": "Неверный или просроченный токен"},
        404: {"description": "Пользователь не найден"},
    },
)
def reset_password(data: ResetPasswordDTO, svc: AuthService = Depends(get_service)):
    svc.reset_password(data.token, data.new_password)
    return {"message": "Пароль успешно изменён"}
