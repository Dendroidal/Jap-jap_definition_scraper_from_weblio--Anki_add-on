These are the available options for this add-on:

*noteTypes*: By default, definition generation while creating/editing cards will only work if the note type has the word "japanese" (case is ignored).
This **does not** affect bulk definition generation while browsing.

*dicSrcFields*: Input fields for the words whose definitions are needed. Different words should be separated by Japanese commas "、". If card contains multiple `dicSrcFields`, only first is used.

*defFields*: Output fields for the fetched definitions. If card contains multiple `defFields`, only first is used.

*sub_definition_count*: For words with multiple sub-definitions, sets the maximum number of sub-definitions to display.

*max_threads*: Number of words that will be fetched simultaneously from weblio.jp. For bulk fetching higher numbers may increase speed, but can also trigger a DDoS protection.

*force_update*: Applies to **bulk definition generation only**. If equal to "no", notes with non-empty `defFields` are ignored. If equal to "overwrite", `defFields` is overwritten with fetched definitions. If equal to "append", fetched definitions are appended to existing ones.

*update_separator*: When `force_update` is "append", this separator is placed between previous content and new content.
 `<br>` inserts a newline.
