from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.test import TestCase
from django.urls import reverse
from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    Expression,
    ExpressionSituation,
    ExpressionUsage,
    LexicalItem,
    SearchAlias,
    SituationFrame,
    Usage,
)


class ModelRelationshipTests(TestCase):
    def test_expression_links_to_usage_not_lexical_item(self):
        lexical_item = LexicalItem.objects.create(headword="available")
        usage = Usage.objects.create(
            lexical_item=lexical_item,
            meaning="人の都合がつく",
        )
        expression = Expression.objects.create(
            text="Are you available tomorrow?",
            japanese_translation="明日都合はつきますか？",
        )

        ExpressionUsage.objects.create(expression=expression, usage=usage)

        self.assertEqual(expression.usages.get(), usage)
        self.assertEqual(usage.lexical_item, lexical_item)
        with self.assertRaises(FieldDoesNotExist):
            Expression._meta.get_field("lexical_items")

    def test_situation_frame_can_be_hierarchical(self):
        parent = SituationFrame.objects.create(name="予定")
        child = SituationFrame.objects.create(name="予定確認", parent=parent)
        expression = Expression.objects.create(text="Does tomorrow work for you?")

        ExpressionSituation.objects.create(expression=expression, situation=child)

        self.assertEqual(child.parent, parent)
        self.assertEqual(expression.situations.get(), child)
        
class ModelConstraintTests(TestCase):
    def test_lexical_item_headword_is_case_insensitive_unique(self):
        LexicalItem.objects.create(headword="available")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                LexicalItem.objects.create(headword="Available")

    def test_search_alias_text_is_case_insensitive_unique(self):
        lexical_item = LexicalItem.objects.create(headword="available")
        SearchAlias.objects.create(lexical_item=lexical_item, text="available")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SearchAlias.objects.create(lexical_item=lexical_item, text="Available")

    def test_expression_usage_can_store_surface_text(self):
        lexical_item = LexicalItem.objects.create(headword="submit")
        usage = Usage.objects.create(
            lexical_item=lexical_item,
            meaning="書類や案を正式に提出する",
        )
        expression = Expression.objects.create(
            text="The proposal was submitted yesterday.",
            japanese_translation="その提案書は昨日提出されました。",
        )

        link = ExpressionUsage.objects.create(
            expression=expression,
            usage=usage,
            surface_text="submitted",
        )

        self.assertEqual(link.surface_text, "submitted")

    def test_expression_usage_is_unique_per_expression_and_usage(self):
        lexical_item = LexicalItem.objects.create(headword="available")
        usage = Usage.objects.create(
            lexical_item=lexical_item,
            meaning="人の都合がつく",
        )
        expression = Expression.objects.create(
            text="Are you available tomorrow?",
            japanese_translation="明日は空いていますか？",
        )

        ExpressionUsage.objects.create(expression=expression, usage=usage)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ExpressionUsage.objects.create(expression=expression, usage=usage)

    def test_root_situation_name_is_unique(self):
        SituationFrame.objects.create(name="会議")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                SituationFrame.objects.create(name="会議")

    def test_situation_cannot_be_its_own_parent(self):
        situation = SituationFrame.objects.create(name="予定確認")
        situation.parent = situation

        with self.assertRaises(ValidationError):
            situation.full_clean()


class SearchAliasCandidateAPITests(APITestCase):
    def setUp(self):
        self.available = LexicalItem.objects.create(headword="available")
        Usage.objects.create(
            lexical_item=self.available,
            meaning="人の都合がつく",
            explanation="予定が空いていて対応できる",
        )
        SearchAlias.objects.create(lexical_item=self.available, text="available")

    def test_returns_existing_alias_candidate_in_expression_text(self):
        response = self.client.post(
            reverse("search-alias-candidates"),
            {"text": "Are you available tomorrow?"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        candidates = response.data["candidates"]
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["search_alias"]["text"], "available")
        self.assertEqual(candidates[0]["lexical_item"]["headword"], "available")
        self.assertEqual(candidates[0]["usages"][0]["meaning"], "人の都合がつく")

    def test_matching_is_case_insensitive_and_long_aliases_are_first(self):
        look_forward_to = LexicalItem.objects.create(headword="look forward to")
        SearchAlias.objects.create(
            lexical_item=look_forward_to,
            text="look forward to",
        )
        forward = LexicalItem.objects.create(headword="forward")
        SearchAlias.objects.create(lexical_item=forward, text="forward")

        response = self.client.post(
            reverse("search-alias-candidates"),
            {"text": "I LOOK forward to hearing from you."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        aliases = [
            candidate["search_alias"]["text"]
            for candidate in response.data["candidates"]
        ]
        self.assertEqual(aliases[:2], ["look forward to", "forward"])

    def test_matching_respects_word_boundaries(self):
        response = self.client.post(
            reverse("search-alias-candidates"),
            {"text": "This item is unavailable."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["candidates"], [])

    def test_candidate_detection_does_not_create_expression_usage_link(self):
        response = self.client.post(
            reverse("search-alias-candidates"),
            {"text": "Are you available tomorrow?"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExpressionUsage.objects.count(), 0)

# Create your tests here.
