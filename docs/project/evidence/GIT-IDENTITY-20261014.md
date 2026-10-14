# Git identity correction — 2026-10-14

The user explicitly requested correcting the four older Codex author/committer
identities to Pranshu Jain with the previously approved GitHub private noreply:
`241415102+pranshujain8532@users.noreply.github.com`.

All seven existing commits retain identical trees, complete messages, author and
committer timestamps/timezones. Only the four identity pairs and descendant parent
IDs changed. All seven commit IDs consequently changed. Historical evidence indexes
and experiment logs retain their original revision IDs; use this map to find the
identical source tree in the corrected main history. Signed artifacts were not edited.

| Original commit | Corrected commit | Changed identity |
|---|---|---|
| `7a58bfe57f55f4d2e0b9d36e953bf3bc93f6a64f` | `36ae345e640db1192a68ceca7f35cedcf7dc01fe` | Author and committer |
| `40a13992483e53d5426d2017e7e9a2461d5dabcb` | `3b59faedfe6f3898e6d168284be9b02726df8713` | Author and committer |
| `fbb5202460660e9ab1c1cc953dc139815a9b026d` | `28fb164ed8e23eb666753c20d391cfcf23e8a9d2` | Author and committer |
| `ffea7be94f4ee19babd9919c4c8767aaf7a2fd69` | `ba9278180a7dd1d638acf147c837af24868a7cae` | Author and committer |
| `e756deb8da8183e54d1b6d60117a6bb9da4fa633` | `d10873cd827b245f3f2c30dc33006a7fec8613ba` | Already correct; parent changed |
| `70d7a012f622124883f14c18bf3f7252f452b422` | `80cb2131610777e48d30141b6436e3d17a6bcf68` | Already correct; parent changed |
| `b8aec154f40c0ed74e03cad8ae529fea75be4ecf` | `63d9595b33ec792e6ba125a4bcf1181156254e67` | Already correct; parent changed |

Verified locally: seven tree/message/date comparisons, exact identity changes,
parent mapping, equal history length, empty old/new tree diff and clean working tree.
The explicit lease-protected push succeeded. Remote `main` was then independently
read as `63d9595b33ec792e6ba125a4bcf1181156254e67`. A first post-push DNS failure
was transient; repeat read succeeded. Context follows in a normal documentation commit.

Local backup ref: `refs/rewind-backups/author-fix-20261014T120906676047Z`.
Ignored raw verification and verified original-history bundle:
`artifacts/git-author-fix/20261014T120906676047Z/verification.json` and
`original-history.bundle` in the same directory. This backup ref was not pushed.

Application tests: **not_run**, because source code and signed evidence did not
change. P5 validation remains the previously recorded evidence, not a new run.
