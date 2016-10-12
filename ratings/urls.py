from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'invite', views.InviteViewSet)
router.register(r'rating', views.RatingViewSet)
router.register(r'webhook', views.HookViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    url(r'^api/v1/user/token/$', views.UserView.as_view(),
        name='create-user-token'),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api/v1/invite/send$',
        views.InviteSend.as_view()),
]
