from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ExpressionSituationViewSet,
    ExpressionUsageViewSet,
    ExpressionViewSet,
    LexicalItemViewSet,
    SearchAliasCandidateAPIView,
    SearchAliasViewSet,
    SituationFrameViewSet,
    UsageViewSet,
)

router = DefaultRouter()
router.register("expressions", ExpressionViewSet)
router.register("lexical-items", LexicalItemViewSet)
router.register("usages", UsageViewSet)
router.register("search-aliases", SearchAliasViewSet)
router.register("situation-frames", SituationFrameViewSet)
router.register("expression-usages", ExpressionUsageViewSet)
router.register("expression-situations", ExpressionSituationViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "search-alias-candidates/",
        SearchAliasCandidateAPIView.as_view(),
        name="search-alias-candidates",
    ),
]
