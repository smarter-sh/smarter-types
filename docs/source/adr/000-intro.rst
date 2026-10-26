ADR Introduction
================

Architectural Decision Records (ADRs) are short documents that capture a single
architectural or design decision, its context, and its consequences. Less is
more: keep them brief. They give this package a version-controlled history of
why it is built the way it is.

See `Michael Nygard's ADRs <https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions.html>`_.

These ADRs use the format of
`Smarter's ADRs <https://github.com/smarter-sh/smarter/tree/main/docs/source/adr>`__.
An ADR that adapts one of Smarter's links it under Related ADRs.

Guidelines for Writing ADRs
---------------------------

- **One decision per ADR.**
- **Be concise.** Focus on clarity and brevity.
- **State the context:** the background and forces that led to the decision.
- **List alternatives**, and why they were not chosen.
- **Explain the decision:** what was decided, and why.
- **Describe consequences**, positive and negative.
- **Use simple language**, for future contributors without today's context.
- **Use the same format** as the others: Status, Context, Decision,
  Alternatives Considered, Consequences, Related ADRs.
- **Reference related ADRs.**
- **Don't rewrite history.** When a decision changes, add an ADR that
  supersedes the old one, and set the old one's status to *Superseded by
  ADR-NNN*.
