# Adding a new ref skill

Loaded on demand by `ref-skills`.


1. **Decide the mode.** Large, binary-backed, or you only disagree with *how it triggers*
   → `wrap`. Small, pure prose, and you intend to change its *content* → `fork`.
2. Write your `SKILL.md`. For a wrap keep it ~40–60 lines: a description that actually
   routes, the overrides, and an explicit pointer to the upstream file and the sections
   to read. Do not restate upstream's procedure — that is the merge tax you are avoiding.
3. Write `REF.md`: `mode`, `source`, `version`, `fingerprint`, `reviewed`, why it exists,
   the overrides that must survive, and the upstream sections you depend on.
   **`version:` is the wrapper's own revision, not the upstream's** — the upstream is
   `source` + `fingerprint` only. See "REF.md fields" below.
4. For a fork, snapshot the base: `mkdir .upstream && cp <upstream> .upstream/SKILL.md`.
5. Add the name to the relevant `loadouts/*.txt` profile (and `loadout.txt` for the
   Claude workstation), run `refsync.py loadout --target ... --profile ... --apply`, then
   `validate_skills.py`.

## REF.md fields

- `mode` — `wrap` or `fork`.
- `source` — `github:<owner>/<repo>@<ref>:<path>`. Pin a commit SHA where you can.
  `upstreams.ini` currently sets `ref = main` for gstack, a moving branch: `@main` plus a
  `fingerprint` records *what you reviewed*, not *which upstream release it was*.
- `version` — **this wrapper's own revision, not the upstream's.** `refsync.py bump_ref`
  rewrites it on `--accept`; nothing reads an upstream version number into it. An upstream
  release string quoted in a SKILL.md body (for example a `gstack vX.Y` citation) is prose
  from the upstream file and is unrelated to this field. If you want the upstream release
  recorded, put the commit SHA in `source`.
- `fingerprint` — sha256 of the upstream file as reviewed. This, with `source`, is the
  only identification of the upstream.
- `reviewed` — the date a human last read the upstream diff.
