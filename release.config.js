// semantic-release, run by .github/workflows/release.yml.
//
// It reads the conventional commits since the last tag (fix: a patch release,
// feat: a minor release, BREAKING CHANGE: a major release), writes the version
// into src/smarter_types/__version__.py, which pyproject.toml reads, updates
// CHANGELOG.md, commits both, tags the commit v<version>, and publishes a
// GitHub release. alpha and beta make prereleases, e.g. 0.2.0-alpha.1, which
// Python's packaging normalizes to 0.2.0a1.
module.exports = {
  branches: [
    "main",
    { name: "beta", prerelease: true },
    { name: "alpha", prerelease: true },
  ],
  plugins: [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    ["@semantic-release/changelog", { changelogFile: "CHANGELOG.md" }],
    [
      "@semantic-release/exec",
      {
        prepareCmd:
          "printf '# DO NOT EDIT.\\n# Managed by semantic-release, through release.config.js.\\n__version__ = \"%s\"\\n' '${nextRelease.version}' > src/smarter_types/__version__.py",
      },
    ],
    [
      "@semantic-release/git",
      {
        assets: ["CHANGELOG.md", "src/smarter_types/__version__.py"],
        message: "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}",
      },
    ],
    "@semantic-release/github",
  ],
};
