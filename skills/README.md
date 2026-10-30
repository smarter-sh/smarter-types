# smarter-types Agent Skills

This folder holds the [Agent Skills](https://agentskills.io/specification) for
working on smarter-types with an AI coding agent such as Claude Code. This
README is written mostly for people.

A skill is a folder of written know-how that an agent loads only when a task
needs it. Each one contains a `SKILL.md` file, and sometimes a `references/`
folder. These skills cover how this repository is built, tested, documented,
released and committed. They are developer tooling, like the `Makefile` and
`.pre-commit-config.yaml`, and the package never loads them.

They follow the skills of [Smarter](https://github.com/smarter-sh/smarter/tree/main/skills)
and of [cache-results](https://github.com/smarter-sh/cache-results/tree/main/skills),
the template of every Smarter PyPI package, so that all of them are developed
the same way. A change here usually continues in the platform (`../smarter`)
and the SDK (`../smarter-python`): load their own skills there.

## What's here

Start with `smarter-types-development`. It sets out the rules that apply to
every change, the package's design, and which narrower skill to load.

| Skill                                  | Use it when                                                                       |
| -------------------------------------- | --------------------------------------------------------------------------------- |
| `smarter-types-development`            | You're making any change, e.g. adding a kind. Start here.                         |
| `smarter-types-testing`                | You're writing or running tests, or raising coverage.                             |
| `smarter-types-docstrings`             | You're writing docstrings, which become the api reference.                        |
| `smarter-types-typing`                 | You're writing type annotations, especially with `Any`.                           |
| `smarter-types-code-quality`           | You're about to finish a change and need to run the pre-commit hooks.             |
| `smarter-types-git-commits`            | You've been asked to write a commit message.                                      |
| `smarter-types-release`                | You're working on CI, Codecov, requirements, semantic-release, PyPI, or the pins. |
| `smarter-types-sphinx-docs`            | You're editing the docs or ADRs, publishing the site, or changing its Terraform.  |
| `blog.smarter.sh-release-announcement` | You're announcing a release on blog.smarter.sh.                                   |
| `blog.smarter.sh-publish`              | You're publishing or updating a post on blog.smarter.sh yourself.                 |

## Claude Code

Claude Code looks for project skills in `.claude/skills/`. This repository
connects the two folders with a committed symlink, `.claude/skills -> ../skills`,
as Smarter's does:

```bash
mkdir -p .claude
ln -s ../skills .claude/skills
```

Other agents that read `SKILL.md` folders can be pointed at this folder, or told
to read `skills/smarter-types-development/SKILL.md` at the start of a session.

## When to add or change a skill

Add to a skill when you've explained the same thing to an agent twice, when a
mistake is costly (e.g. a renamed member that breaks the platform, the SDK and
every manifest that names it), when a pattern isn't obvious from the code, or
when checking a change takes a fragile series of steps. Don't add one for what
the code, the linters or CI already enforce, for one-off facts, or for personal
preferences. Prefer editing an existing skill to adding one, and keep each
`SKILL.md` short.

## Security considerations

A skill is a set of instructions that an agent follows, often without asking.
**Review a change to this folder as carefully as a change to CI.**

- **Some instructions forbid things on purpose**, e.g. never running
  `git commit`, or applying Terraform without a plan the user has seen. Don't
  remove a rule like that unless you mean to give agents that power.
- **The docs site's Terraform changes live AWS resources** in a shared account
  and DNS zone. The skills require a reviewed plan before every apply.
- **Skills can carry prompt injection.** Look for instructions unrelated to a
  skill's purpose, new scripts with network calls, and text that tells an agent
  to skip confirmations, hooks or safety rules.
- **`blog.smarter.sh-publish` signs in to the blog as an administrator.** Its
  `wp.py` makes network calls to blog.smarter.sh with the credentials in
  `../smarter/.env`, and publishing is public. The skill publishes only when
  asked, and uploads a draft otherwise.
- **Keep secrets out.** This repository is public: no credentials, account ids,
  private hostnames or customer data in a skill or an example.
