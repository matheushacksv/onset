from ninja_extra import NinjaExtraAPI
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.controller import NinjaJWTDefaultController

# Import routers
from accounts.api import router as auth_router
from onboarding.api import router as onboarding_router
from onboarding.knowledge_api import router as knowledge_router

api = NinjaExtraAPI(auth=JWTAuth())

# Auth controler
api.register_controllers(NinjaJWTDefaultController)

# Add routers
api.add_router('auth/', auth_router)
api.add_router('onboarding/', onboarding_router)
api.add_router('knowledge/', knowledge_router)
