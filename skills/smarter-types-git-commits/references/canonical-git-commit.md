# Canonical Git Commit

An illustrative example in the required format, not a real commit: one that
adds a SAM kind. Replace its counts with your own. What makes
it a good one:

- The type is `feat`, because it adds a kind that users can write manifests
  of. semantic-release counts it as a minor release.
- The first paragraph explains why the change exists, and what it does not do
  yet (the platform and the SDK still need their minimum version raised).
- Each area gets a heading paragraph, then one bullet per change, with the
  reason for each non-obvious decision, e.g. why the kind goes where it does
  in the apply order.
- The tests are described by what they prove, not just listed.
- It ends with the status: what was run, and what is not done yet.
- Lawrence McDaniel is the author, and Claude is the co-author.

Note that the body can't use backticks, `$` or `!`: they are inside double
quotes in zsh.

```console
git commit --author="Lawrence McDaniel <lpm0073@gmail.com>" \
  -m "feat(kinds): add the Orchestrator kind" \
  -m "The platform is adding an Orchestrator resource, whose manifests coordinate several LLMClients. The platform and the SDK both need to know the kind exists, so it is added here, where SAMKinds is defined once for both. Neither uses it yet: each needs its minimum version of smarter-types raised after this release." \
  -m "Kinds (src/smarter_types/kinds.py):" \
  -m "- SAMKinds.ORCHESTRATOR, with the value Orchestrator, in the prompt resources group.
- apply_order() places it after LLMClient and Prompt and before Budget: each of its spec.config.harnesses names an LLMClient by llmClientName, and a Budget can name an Orchestrator. The method's docstring gains its numbered entry." \
  -m "Journal (src/smarter_types/journal.py):" \
  -m "- SmarterJournalThings.ORCHESTRATOR takes its value from SAMKinds.ORCHESTRATOR, and is added to choices()." \
  -m "Tests: test_kinds.py checks that every kind, the new one included, has an apply rank, a plural and a journal thing, and that Orchestrator sorts after LLMClient and before Budget." \
  -m "Status: 64 tests pass with 100% coverage on Python 3.10 and 3.14, mypy and the pre-commit hooks pass, and the docs build without warnings. Not yet done: raising the minimum version of smarter-types in smarter and smarter-python." \
  -m "Co-authored-by: Claude <noreply@anthropic.com>"
```
