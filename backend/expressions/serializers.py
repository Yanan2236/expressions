from rest_framework import serializers

from .models import (
    Expression,
    ExpressionSituation,
    ExpressionUsage,
    LexicalItem,
    SearchAlias,
    SituationFrame,
    Usage,
)


class ExpressionSerializer(serializers.ModelSerializer):
    usage_ids = serializers.PrimaryKeyRelatedField(
        source="usages",
        many=True,
        read_only=True,
    )
    situation_ids = serializers.PrimaryKeyRelatedField(
        source="situations",
        many=True,
        read_only=True,
    )

    class Meta:
        model = Expression
        fields = [
            "id",
            "text",
            "japanese_translation",
            "note",
            "usage_ids",
            "situation_ids",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "usage_ids", "situation_ids", "created_at", "updated_at"]


class LexicalItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LexicalItem
        fields = ["id", "headword", "item_type", "note", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class UsageSerializer(serializers.ModelSerializer):
    lexical_item_headword = serializers.CharField(
        source="lexical_item.headword",
        read_only=True,
    )

    class Meta:
        model = Usage
        fields = [
            "id",
            "lexical_item",
            "lexical_item_headword",
            "meaning",
            "explanation",
            "example",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "lexical_item_headword", "created_at", "updated_at"]


class SearchAliasSerializer(serializers.ModelSerializer):
    lexical_item_headword = serializers.CharField(
        source="lexical_item.headword",
        read_only=True,
    )

    class Meta:
        model = SearchAlias
        fields = [
            "id",
            "lexical_item",
            "lexical_item_headword",
            "text",
            "note",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "lexical_item_headword", "created_at", "updated_at"]


class SituationFrameSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent.name", read_only=True)

    class Meta:
        model = SituationFrame
        fields = [
            "id",
            "name",
            "parent",
            "parent_name",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "parent_name", "created_at", "updated_at"]

    def validate_parent(self, parent):
        if self.instance and parent and parent.pk == self.instance.pk:
            raise serializers.ValidationError("A situation cannot be its own parent.")
        return parent


class ExpressionUsageSerializer(serializers.ModelSerializer):
    expression_text = serializers.CharField(source="expression.text", read_only=True)
    usage_meaning = serializers.CharField(source="usage.meaning", read_only=True)
    lexical_item_headword = serializers.CharField(
        source="usage.lexical_item.headword",
        read_only=True,
    )

    class Meta:
        model = ExpressionUsage
        fields = [
            "id",
            "expression",
            "expression_text",
            "usage",
            "usage_meaning",
            "lexical_item_headword",
            "surface_text",
            "note",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "expression_text",
            "usage_meaning",
            "lexical_item_headword",
            "created_at",
        ]


class ExpressionSituationSerializer(serializers.ModelSerializer):
    expression_text = serializers.CharField(source="expression.text", read_only=True)
    situation_name = serializers.CharField(source="situation.name", read_only=True)

    class Meta:
        model = ExpressionSituation
        fields = [
            "id",
            "expression",
            "expression_text",
            "situation",
            "situation_name",
            "note",
            "created_at",
        ]
        read_only_fields = ["id", "expression_text", "situation_name", "created_at"]


class SearchAliasCandidateRequestSerializer(serializers.Serializer):
    text = serializers.CharField()
