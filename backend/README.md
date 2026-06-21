# Expressions Backend

This backend stores English expression cards and links them to meanings through usages.

Important design rule: `Expression` does not link directly to `LexicalItem`. A lexical item is only the word, phrase, or chunk itself. Meanings and ways of use belong to `Usage`, and an expression links to a usage through `ExpressionUsage`.

`SearchAlias` is only for candidate detection. Matching an alias in text returns a candidate from the API, but it never creates an `ExpressionUsage` link automatically.

Main API routes are under `/api/`:

- `/api/expressions/`
- `/api/lexical-items/`
- `/api/usages/`
- `/api/search-aliases/`
- `/api/situation-frames/`
- `/api/expression-usages/`
- `/api/expression-situations/`
- `/api/search-alias-candidates/`
