# Guides YAML Schema (guides/*.yaml)

## Top-level fields
- `id` (string)
- `title` (string)
- `summary` (string)
- `tags` (list of strings)
- `keywords` (list of strings)
- `sections` (list of section objects)
- `resources` (list of resource objects)

## Section object
- `title` (string)
- `body` (list of strings)
- `tips` (list of strings, optional)
- `highlights` (list of strings, optional)

## Resource object
- `title` (string)
- `url` (string)
