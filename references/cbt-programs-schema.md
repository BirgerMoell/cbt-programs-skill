# CBT Program YAML Schema (cbt-programs/*.yaml)

## Top-level fields
- `id` (string)
- `title` (string)
- `condition` (string)
- `summary` (string)
- `duration` (string)
- `focusAreas` (list of strings)
- `modules` (list of module objects)

## Module object
- `title` (string)
- `overview` (list of strings)
- `takeaways` (list of strings)
- `narrative` (list of narrative objects)
- `exercises` (list of strings)
- `homework` (list of strings)

## Narrative object
- `section` (string)
- `paragraphs` (list of strings)
- `exerciseAfter` (integer, optional)
  - If present, indicates an exercise index (0-based) to emphasize after this section.
