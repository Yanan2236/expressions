from django.contrib import admin

from .models import (
    Expression,
    ExpressionSituation,
    ExpressionUsage,
    LexicalItem,
    SearchAlias,
    SituationFrame,
    Usage,
)


class ExpressionUsageInline(admin.TabularInline):
    model = ExpressionUsage
    extra = 0
    autocomplete_fields = ["usage"]


class ExpressionSituationInline(admin.TabularInline):
    model = ExpressionSituation
    extra = 0
    autocomplete_fields = ["situation"]


class UsageInline(admin.TabularInline):
    model = Usage
    extra = 0


class SearchAliasInline(admin.TabularInline):
    model = SearchAlias
    extra = 0


@admin.register(Expression)
class ExpressionAdmin(admin.ModelAdmin):
    list_display = ["id", "short_text", "created_at", "updated_at"]
    search_fields = ["text", "japanese_translation", "note"]
    inlines = [ExpressionUsageInline, ExpressionSituationInline]

    def short_text(self, obj):
        return obj.text[:80]


@admin.register(LexicalItem)
class LexicalItemAdmin(admin.ModelAdmin):
    list_display = ["id", "headword", "created_at", "updated_at"]
    search_fields = ["headword", "note"]
    inlines = [UsageInline, SearchAliasInline]


@admin.register(Usage)
class UsageAdmin(admin.ModelAdmin):
    list_display = ["id", "lexical_item", "meaning", "created_at", "updated_at"]
    list_filter = ["lexical_item"]
    search_fields = ["meaning", "explanation", "example", "note", "lexical_item__headword"]
    autocomplete_fields = ["lexical_item"]


@admin.register(SearchAlias)
class SearchAliasAdmin(admin.ModelAdmin):
    list_display = ["id", "text", "lexical_item", "created_at", "updated_at"]
    list_filter = ["lexical_item"]
    search_fields = ["text", "note", "lexical_item__headword"]
    autocomplete_fields = ["lexical_item"]


@admin.register(SituationFrame)
class SituationFrameAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "parent", "created_at", "updated_at"]
    list_filter = ["parent"]
    search_fields = ["name", "description"]
    autocomplete_fields = ["parent"]


@admin.register(ExpressionUsage)
class ExpressionUsageAdmin(admin.ModelAdmin):
    list_display = ["id", "expression", "usage", "created_at"]
    list_filter = ["usage__lexical_item"]
    search_fields = ["expression__text", "usage__meaning", "usage__lexical_item__headword"]
    autocomplete_fields = ["expression", "usage"]


@admin.register(ExpressionSituation)
class ExpressionSituationAdmin(admin.ModelAdmin):
    list_display = ["id", "expression", "situation", "created_at"]
    list_filter = ["situation"]
    search_fields = ["expression__text", "situation__name"]
    autocomplete_fields = ["expression", "situation"]
