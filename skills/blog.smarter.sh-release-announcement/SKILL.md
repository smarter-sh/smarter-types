---
name: blog.smarter.sh-release-announcement
description: Use when asked to write or publish a release announcement, release notes post, or blog post for a release of smarter-types on PyPI (e.g. "announce smarter-types v0.1"), for blog.smarter.sh. Covers finding the releases that no post has announced yet, gathering the material from CHANGELOG.md and the full commit bodies between two release tags, checking every example against the release installed from PyPI, the post's structure (install command, summary table, using it, what changed, how it's built and released, try it, what's next), the writing style, public-repo hygiene, and what to check before publishing it with blog.smarter.sh-publish.
---

# blog.smarter.sh Release Announcement for smarter-types

A release post on [blog.smarter.sh](https://blog.smarter.sh) tells Python
developers what a release of smarter-types lets them do, and what they must do to
upgrade. It's written in Markdown, saved outside the repository, and published
with `blog.smarter.sh-publish`. It is not part of the docs, and it is not
committed.

This skill is adapted from the one in
[Smarter's skills](https://github.com/smarter-sh/smarter/tree/main/skills/blog.smarter.sh-release-announcement),
which announces releases of the platform. A package's post is shorter, shows
Python instead of manifests, and is about a library that people install, not a
platform that they run.

[references/example-cache-results-v0.1.md](references/example-cache-results-v0.1.md)
is a package announcement that the user published. Read it before writing,
and match its structure and voice. Then read the most recent posts in the
[Announcements](https://blog.smarter.sh/category/announcements/) category, so
the new post fits beside them.

## 1. Find what to announce

Releases aren't announced one by one. A post covers every release since the
last one that was announced, so first find that one:

```bash
skills/blog.smarter.sh-publish/scripts/wp.py list --status any --search "smarter-types"
```

Announcements are in category 4, with titles that start with `smarter-types vX.Y`. If
there's none, the post is the package's first announcement, and it has to
introduce the package too. Then list the tags (`git tag --sort=-creatordate`)
and check the latest release on PyPI
(`https://pypi.org/pypi/smarter-types/json`): announce only what PyPI has. Alpha and
beta releases are part of the stable release that follows them, never posts of
their own.

## 2. Gather the material

`CHANGELOG.md`, which semantic-release writes, lists one-line commit subjects.
The commit bodies explain what each change is, why it exists, its limits and
its upgrade steps, and that is what the post is made of. Print every commit
between the last announced tag and the release, oldest first, without the
release commits:

```bash
skills/blog.smarter.sh-release-announcement/scripts/release-sources.sh v0.1.0 v0.2.0
```

Read the `ci:`, `build:` and `docs:` commits too, which the changelog leaves
out. They often explain how the package is built, tested and released, which
belongs in the post's "built to be depended on" section.

Then read the package's docs (`docs/source/`, published at
https://docs.smarter-types.smarter.sh/) for the pages to link.

## 3. Check every example against the release

The reader will copy the code. Install the announced version from PyPI into a
throwaway virtual environment in your scratchpad, not the repository's own
venv, and run every example in the post against it:

```bash
python3 -m venv <scratchpad>/venv-announce
<scratchpad>/venv-announce/bin/pip install "smarter-types==X.Y.Z"
```

An example that needs a server, such as a Smarter platform or Redis, runs
against a local one. If you can't run an example, say so in your reply.

## 4. Structure

In this order, as in the example:

1. **Title:** `# smarter-types vX.Y Release: <the release's theme in a few words>`,
   then a date line, `Month D, YYYY · The Smarter Project`. The H1 becomes
   the WordPress title, and `blog.smarter.sh-publish` leaves both out of the
   post's content, because the theme prints the title and date. For a range,
   `# smarter-types vX.Y – vX.Z Release: ...`, with an en dash.
2. **The opening:** what the release lets the reader do, in one or two short
   paragraphs, and the install command, `pip install --upgrade smarter-types`. A
   first announcement says what the package is, who it's for, and how it
   relates to Smarter.
3. **A summary table** of what you get, one sentence each, with a bold
   lead-in. A reader who stops here should still know what shipped.
4. **Using it:** real, short Python that the reader can run, followed by the
   rules worth knowing as bullets with a bold lead-in. End the section with
   `📖 [smarter-types documentation](https://docs.smarter-types.smarter.sh/)`.
5. **What changed**, for a release after the first: one bullet per change,
   saying what was wrong or missing and what happens now. Breaking changes and
   renamed imports go first, with what to change in your code.
6. **Built to be depended on:** the supported Python (and Django) versions,
   typing, tests and coverage, how it's released (trusted publishing,
   TestPyPI rehearsal, provenance), and the docs site. Keep only what's true
   of this release, and only what changed if an earlier post already said it.
7. **Try it, and tell people about it:** install it, star the repository,
   open an issue, and a link to Smarter.
8. **What's next**, then a closing line that links the changelog
   (`https://github.com/smarter-sh/smarter-types/blob/main/CHANGELOG.md`), the
   release on GitHub, PyPI, the docs and the repository.

Separate the major sections with `---`.

## 5. Style

- Write for Python developers who use or are evaluating the package, not for
  its contributors. Leave out internal detail with no visible effect.
- Plain words, short sentences and exact facts: versions, setting names,
  error types, numbers.
- Be honest about the past. "The previous release did X, which caused Y" is
  more credible than presenting a fix as a feature.
- Use headings, not bold lines, as section labels, and blank lines around
  lists (MD036, MD032).
- No emoji except the 📖 docs link.
- Code fences need a language that the blog highlights: `python`, `bash`,
  `yaml` or `plain`. See `blog.smarter.sh-publish`.

## 6. Public-repo hygiene

The post is published, and this skill lives in a public repository. Commit
bodies sometimes name hosts, accounts or tokens. Never copy them into the
post.

## 7. Before publishing

- Every example ran against the release installed from PyPI.
- Every claim traces to a commit body or the changelog. "What's next" is
  usually a guess: say so in your reply.
- Every docs link's page exists under `docs/source/`.
- Save the post to `~/desktop/blog-release-smarter-types-vX-Y.md`, never inside the
  repository or only in your scratchpad.
- Publish it with `blog.smarter.sh-publish`: slug `release-smarter-types-vX-Y`,
  category 4, no featured image (announcements have none). Publish it live
  only when the user asked you to publish. Otherwise upload a draft.
- In your reply, give the post's link, the releases it covers, and what to
  review: guessed content, anything you couldn't run, anything you left out
  on purpose.
