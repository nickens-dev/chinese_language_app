# Dictionary-Assisted Entry

Dictionary assistance enriches the manual card editor without bypassing learner review. Search accepts English, simplified or traditional characters, numbered pinyin, and tone-marked pinyin.

## Provider pipeline

1. The backend reads the CC-CEDICT data bundled by `chinese-english-lookup` with an application-owned UTF-8 parser. This avoids the package's Windows default-encoding defect while retaining its packaged dictionary.
2. Exact matches rank before prefixes and substring matches. Search covers simplified, traditional, pinyin, and English definitions.
3. CC-CEDICT's explicit simplified/traditional pair, pronunciation, and definitions remain authoritative when present.
4. `opencc-python-reimplemented` supplies script conversion only when no dictionary entry matches Chinese input.
5. `pypinyin` supplies contextual pronunciation for that same fallback.
6. The editor applies a selected candidate to ordinary editable card fields. Nothing is saved until the learner submits the card form.

The provider is isolated behind `CedictProvider`; future dictionary sources or ML ranking can replace or augment it without changing the API or persisted card shape.

## Pinyin handling

CC-CEDICT stores numbered pinyin. The application converts each syllable to standard tone marks, including the `a/e/ou` placement rules and `v`/`u:` input for `ü`. Search normalizes numbered and tone-marked input to the same comparison form.

## Provenance

Cards store `source_name` and `source_entry_id`. Manual cards use `user`; CC-CEDICT candidates use a stable content-derived entry identifier. Editing an imported candidate does not erase its origin.

## Data attribution

The bundled dictionary identifies itself as CC-CEDICT, published by MDBG under the Creative Commons Attribution-ShareAlike 4.0 International License. The application must retain this attribution in documentation and in any future export or redistribution of sourced dictionary content.

- Project: https://www.mdbg.net/chinese/dictionary?page=cc-cedict
- License: https://creativecommons.org/licenses/by-sa/4.0/

Package code has its own licenses; those do not replace the dictionary-data license.

## Performance

The dictionary is parsed lazily on the first search and cached for the backend process. On the current development machine, the first load takes roughly four seconds; subsequent searches generally complete within a fraction of a second. A future optimization can build a versioned SQLite search index during installation or migration.