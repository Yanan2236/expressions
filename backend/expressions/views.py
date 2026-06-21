from rest_framework import mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Expression,
    ExpressionSituation,
    ExpressionUsage,
    LexicalItem,
    SearchAlias,
    SituationFrame,
    Usage,
)
from .serializers import (
    ExpressionSerializer,
    ExpressionSituationSerializer,
    ExpressionUsageSerializer,
    LexicalItemSerializer,
    SearchAliasCandidateRequestSerializer,
    SearchAliasSerializer,
    SituationFrameSerializer,
    UsageSerializer,
)
from .services import find_search_alias_candidates


class ExpressionViewSet(viewsets.ModelViewSet):
    queryset = Expression.objects.all()
    serializer_class = ExpressionSerializer
    search_fields = ["text", "japanese_translation", "note"]
    ordering_fields = ["created_at", "updated_at", "id"]


class LexicalItemViewSet(viewsets.ModelViewSet):
    queryset = LexicalItem.objects.all()
    serializer_class = LexicalItemSerializer
    search_fields = ["headword", "note"]
    ordering_fields = ["headword", "created_at", "updated_at", "id"]


class UsageViewSet(viewsets.ModelViewSet):
    queryset = Usage.objects.select_related("lexical_item").all()
    serializer_class = UsageSerializer
    filterset_fields = ["lexical_item"]
    search_fields = ["meaning", "explanation", "example", "note", "lexical_item__headword"]
    ordering_fields = ["meaning", "created_at", "updated_at", "id"]


class SearchAliasViewSet(viewsets.ModelViewSet):
    queryset = SearchAlias.objects.select_related("lexical_item").all()
    serializer_class = SearchAliasSerializer
    filterset_fields = ["lexical_item"]
    search_fields = ["text", "note", "lexical_item__headword"]
    ordering_fields = ["text", "created_at", "updated_at", "id"]


class SituationFrameViewSet(viewsets.ModelViewSet):
    queryset = SituationFrame.objects.select_related("parent").all()
    serializer_class = SituationFrameSerializer
    filterset_fields = ["parent"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at", "updated_at", "id"]


class ExpressionUsageViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ExpressionUsage.objects.select_related(
        "expression",
        "usage",
        "usage__lexical_item",
    ).all()
    serializer_class = ExpressionUsageSerializer
    filterset_fields = ["expression", "usage", "usage__lexical_item"]


class ExpressionSituationViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ExpressionSituation.objects.select_related(
        "expression",
        "situation",
    ).all()
    serializer_class = ExpressionSituationSerializer
    filterset_fields = ["expression", "situation"]


class SearchAliasCandidateAPIView(APIView):
    def post(self, request):
        serializer = SearchAliasCandidateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        candidates = find_search_alias_candidates(serializer.validated_data["text"])
        return Response({"candidates": candidates}, status=status.HTTP_200_OK)
