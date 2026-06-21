from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower


class Expression(models.Model):
    text = models.TextField()
    japanese_translation = models.TextField(blank=True)
    note = models.TextField(blank=True)
    usages = models.ManyToManyField(
        "Usage",
        through="ExpressionUsage",
        related_name="expressions",
        blank=True,
    )
    situations = models.ManyToManyField(
        "SituationFrame",
        through="ExpressionSituation",
        related_name="expressions",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return self.text[:80]


class LexicalItem(models.Model):
    class ItemType(models.TextChoices):
        WORD = "word", "単語"
        PHRASE = "phrase", "熟語"
        CHUNK = "chunk", "チャンク"
        
    headword = models.CharField(max_length=255)
    item_type = models.CharField(
        max_length=20,
        choices=ItemType.choices,
        default=ItemType.WORD,
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["headword"]
        constraints = [
            UniqueConstraint(Lower("headword"), name="unique_lexical_item_headword_ci"),
        ]

    def __str__(self):
        return self.headword


class Usage(models.Model):
    lexical_item = models.ForeignKey(
        LexicalItem,
        on_delete=models.CASCADE,
        related_name="usages",
    )
    meaning = models.CharField(max_length=255)
    explanation = models.TextField(blank=True)
    example = models.TextField(blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["lexical_item__headword", "meaning"]
        constraints = [
            models.UniqueConstraint(
                fields=["lexical_item", "meaning"],
                name="unique_usage_meaning_per_lexical_item",
            ),
        ]

    def __str__(self):
        return f"{self.lexical_item}: {self.meaning}"


class SearchAlias(models.Model):
    lexical_item = models.ForeignKey(
        LexicalItem,
        on_delete=models.CASCADE,
        related_name="search_aliases",
    )
    text = models.CharField(max_length=255)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["text"]
        verbose_name_plural = "search aliases"
        constraints = [
            UniqueConstraint(Lower("text"), name="unique_search_alias_text_ci"),
        ]

    def __str__(self):
        return self.text


class SituationFrame(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        null=True,
        blank=True,
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["parent", "name"],
                name="unique_situation_name_per_parent",
                nulls_distinct=False,
            ),
        ]

    def clean(self):
        super().clean()
        if self.pk and self.parent_id == self.pk:
            raise ValidationError({"parent": "A situation cannot be its own parent."})

    def __str__(self):
        return self.name


class ExpressionUsage(models.Model):
    expression = models.ForeignKey(
        Expression,
        on_delete=models.CASCADE,
        related_name="usage_links",
    )
    usage = models.ForeignKey(
        Usage,
        on_delete=models.CASCADE,
        related_name="expression_links",
    )
    surface_text = models.CharField(max_length=255, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["expression", "usage"],
                name="unique_expression_usage",
            ),
        ]

    def __str__(self):
        return f"{self.expression} -> {self.usage}"


class ExpressionSituation(models.Model):
    expression = models.ForeignKey(
        Expression,
        on_delete=models.CASCADE,
        related_name="situation_links",
    )
    situation = models.ForeignKey(
        SituationFrame,
        on_delete=models.CASCADE,
        related_name="expression_links",
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["expression", "situation"],
                name="unique_expression_situation",
            ),
        ]

    def __str__(self):
        return f"{self.expression} -> {self.situation}"
