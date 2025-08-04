<!-- @@@title:Backend Indexer Settings@@@ -->

As noted in <a href="/help/administration/backend_configuration_options">Backend Configuration Options</a> section, the default settings for the full text indexer are set to:

| Setting                         | Default Value                     
|---------------------------------|---------------
| SPHINX_MIN_WORD_LENGTH          | 4                                 
| SPHINX_MIN_PREFIX_LENGTH        | 4                                 
| SPHINX_MIN_INFIX_LENGTH         | 4 *(0 for versions earlier than v6.15.0)*

In order to use prefix wildcard searching, you must enable `SPHINX_MIN_INFIX_LENGTH` by setting it to match the values used for `SPHINX_MIN_WORD_LENGTH` and `SPHINX_MIN_PREFIX_LENGTH`. For example:

    logzilla config SPHINX_MIN_INFIX_LENGTH 4
  
>Note: After changing these values, the settings are only applied on incoming events, not on events already stored in the system.

Infix indexing allows prefix wildcard searching, for example: `*end`, and `*middle*` wildcards (LogZilla already allows suffix wildcards by default, e.g.: `start*`). When the minimum infix length is set to a positive number, the indexer will index all possible keyword infixes (ie. substrings) in addition to the keywords themselves. Too short infixes (below the minimum allowed length) will not be indexed. For example, indexing a keyword `test` with `SPHINX_MIN_INFIX_LENGTH=2` would result in indexing `te`, `es`, `st`, `tes`, `est` along with the word itself. Searches against such an index for `es` would match events that contain the word `test` even if it does not contain `es` itself.
> Caution! Indexing infixes will make the index grow significantly (because of many more indexed keywords) and can degrade both indexing and searching times dramatically.  This will (possibly greatly) increase memory usage, which will contribute to performance degradation.
> Setting a value < 4 is **highly discouraged**
