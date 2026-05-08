# Ninja imports
from ninja import Router, File, Status
from ninja import UploadedFile
from ninja_jwt.tokens import RefreshToken
# Django enconding
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
# Django Storage
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
# Django Shortcuts
from django.shortcuts import get_object_or_404
# Models and Schemas imports
from .models import User
from .schemas import LoginIn, UserOut, UpdateMeIn, TokenOut, RefreshIn, ResetPasswordIn, ForgotPasswordIn, CreateUserIn, UpdateUserIn
from core.errors import Error
# Django Auth imports
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
# Accounts Tasks
from django_q.tasks import async_task
# UUID
import uuid

router = Router(tags=['Auth'])


@router.post('/login', response={200: TokenOut, 401: Error}, auth=None)
def user_login(request, data: LoginIn):
    '''User login endpoint'''

    user = authenticate(request, username=data.email, password=data.password)

    if not user:
        return Status(401, Error(detail='Invalid email or password'))

    refresh = RefreshToken.for_user(user)

    return Status(200, TokenOut(access=str(refresh.access_token), refresh=str(refresh)))

@router.post('/refresh', response={200: TokenOut, 401: Error}, auth=None)
def refresh_token(request, data: RefreshIn):
    '''Refresh token endpoint'''

    try:
        refresh = RefreshToken(data.refresh)
        return Status(200, TokenOut(access=str(refresh.access_token), refresh=str(refresh)))
    except Exception as e:
        return Status(401, Error(detail=f'Invalid ou expired token: {e}'))

@router.get('/me', response=UserOut)
def me(request):
    '''Me endpoint'''

    return User.objects.get(id=request.auth.id)

@router.put('/me', response={200: UserOut, 400: Error})
def update_me(request, data: UpdateMeIn):
    '''Update user information'''

    user = request.auth

    if data.new_password:
        if not user.check_password(data.current_password):
            return Status(400, Error(detail='Incorret password'))
        user.set_password(data.new_password)

    if data.name:
        user.name = data.name

    user.save()
    return user

@router.post('/me/avatar', response={200: UserOut})
def upload_avatar(request, file: UploadedFile = File()):
    '''Upload avatar to user information'''

    user = request.auth

    mime = file.content_type or 'application/octet-stream'
    ext = mime.split('/')[-1].split(';')[0]
    path = default_storage.save(
        f'avatars/{uuid.uuid4()}.{ext}',
        ContentFile(file.read())
    )

    url = default_storage.url(path)
    user.avatar = url
    user.save()
    return Status(200, user)

@router.post('/forgot-password', response={200: dict}, auth=None)
def forgot_password(request, data: ForgotPasswordIn):
    '''Forgot password endpoint reset'''

    user = User.objects.filter(email=data.email).first()

    if user:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_url = f'{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}'

        async_task('accounts.tasks.send_reset_email', user.email, reset_url)
        
    return Status(200, {'detail': 'Se o email existir, você receberá um link em breve.'})

@router.post('/reset-password', response={200: dict, 400: Error})
def reset_password(request, data: ResetPasswordIn):
    '''Reset password endpoint'''
    
    try:
        uid = force_str(urlsafe_base64_decode(data.uid))
        user = User.objects.get(pk=uid)
    except Exception:
        return Status(400, Error(detail='Token inválido'))

    if not default_token_generator.check_token(user, data.token):
        return Status(400, Error(detail='Token inválido ou expirado'))

    user.set_password(data.password)
    user.save()
    return Status(200, {'detail': 'Senha redefinida com sucesso'})

@router.get('/users', response=list[UserOut])
def list_users(request):
    qs = User.objects.prefetch_related('groups').order_by('name')
    if not (request.auth.is_superuser or request.auth.is_staff):
        qs = qs.filter(is_active=True)
    return qs

@router.post('/create-user', response={201: UserOut, 400: Error})
def create_user(request, data: CreateUserIn):
    
    if User.objects.filter(email=data.email).exists():
        return Status(400, Error(detail='Já existe usuário com esse email'))
    user = User.objects.create_user(
        email=data.email, 
        password=data.password, 
        name=data.name or '',
        is_staff=bool(data.is_staff)
        )
    if data.role:
        user.groups.set(Group.objects.filter(name__in=data.role))

    return Status(201, user)

@router.get('/roles', response=list[str])
def list_roles(request):
    return list(Group.objects.values_list('name', flat=True).order_by('name'))

@router.patch('/{user_id}', response={200: UserOut, 403: Error, 404: Error})
def edit_member(request, user_id: int, data: UpdateUserIn):
    if not request.auth.is_superuser:
        return Status(403, Error(detail='Não autorizado'))
    user = get_object_or_404(User, id=user_id)
    if user.id == request.auth.id and data.is_active is False:
        return Status(400, Error(detail='Não pode desativar a própria conta'))
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.is_staff is not None:
        user.is_staff = data.is_staff
    user.save()
    if data.role is not None:
        user.groups.set(Group.objects.filter(name__in=data.role))
    return Status(200, user)
