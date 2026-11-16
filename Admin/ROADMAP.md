# Pynsource roadmap and release status

Current stable: **1.86** (November 2026). Previous stable: 1.84 (2022); 1.85 was a beta series.

This file is the durable, public-safe summary: what is shipping, what is next, and how the
canvas libraries relate. Detailed working notes stay outside the repo (this repo is public, so
no licence internals or store credentials here).

Related docs: [BUILDING.md](../BUILDING.md) (build, test, CI), [DOWNLOADS.md](../DOWNLOADS.md)
(user install + troubleshooting), [AGENTS.md](../AGENTS.md) (contributor/session notes),
[CHANGELOG.md](../CHANGELOG.md) (what shipped).

## 1.86 — release train (current)

Every packaging route was built and verified on the `2026-dustoff` branch before it was merged
to `master`; the merge is what this release formalises.

| Phase | Scope | State |
|---|---|---|
| 1 | macOS CI (`build-mac.yml`), uv python-build-standalone, onedir `.app` | done |
| 2 | Homebrew cask `abulka/pynsource/pynsource` with quarantine-strip postflight | done |
| 3 | Windows CI + Inno Setup 6 installer | done |
| 4 | AppImage x86_64 + aarch64 via linuxdeploy | done |
| 5 | Snap: core24, both arches, edge upload from CI | done, user-verified |
| 6 | Flatpak / Flathub | **deferred** — see milestones |
| 7 | Docs consolidation (README / DOWNLOADS / BUILDING) | done |
| 8 | Merge to `master`, version 1.86, tag, publish, promote | **published 2026-11-16** |

Published as <https://github.com/abulka/pynsource/releases/tag/version-1.86> with both AppImages,
the macOS zip and the Windows installer. Still to do:

1. Promote snap revisions **34** (amd64) and **35** (arm64) from `edge` to `stable` in the store
   UI, then drop the "edge while being tested" wording in README/DOWNLOADS.
2. Sanity-check zoom speed on bare metal (mac + a real Linux desktop). A GPU-less VM is the
   worst case for a `PaintDC` canvas and is not evidence of a regression.
3. Optional tidy: delete the old `pre-*` releases except the most recent.

## The canvas libraries: ogl2 (frozen) and wxdiagram (future)

Pynsource has two canvases and they are chosen by edition in `src/gui/settings.py`:

| Edition | Canvas | Where it lives |
|---|---|---|
| Community | vendored classic OGL | `src/ogl/` in this repo |
| Pro / Linux | `ogl2` | separate repo `abulka/ogl2` |

`ogl2` is now **frozen at `2026-dustoff`**, which is its `master` head. It is MIT, carries the
OGL-like shape/connector canvas (zoom, pan, drag-to-connect, JSON persistence) and is bundled
into the Linux artefacts, where Pro is free.

Its successor is **`wxdiagram`** — a clean-history library built from the ogl2 `standalone`
work, with the package renamed and the pynsource/app debris removed (`pro/`, `bin/`, `media/`,
`CodeBlock`, `ContainerBlock`). It is *not* a dependency of pynsource 1.x:

- **pynsource 1.x uses `ogl2`** and will keep doing so.
- **pynsource 2.x will use `wxdiagram`** and drop `ogl2`.
- No release may depend on both.

Consequence for later cleanup: the PyInstaller spec, mac/win build scripts and the `.icns`
icon still live in `ogl2` (`bin/`, `media/`) because that is where they grew up. They must move
into this repo **before `ogl2` is archived**; until then, a spec change only reaches CI once it
is pushed to `ogl2`.

## Milestones

| Milestone | Content | Notes |
|---|---|---|
| 1.86 | First stable release since 1.84; all platforms built by CI | now |
| 1.86.x | Patch releases via `PATCH` in `src/gui/settings.py` | no retagging |
| wxdiagram 0.1.0 | Renamed library, correctness pass from the OGL comparison, docs site | own repo, own release |
| pynsource 2.0 | Port the Pro canvas to `wxdiagram`; `ogl2` archived | planned, not started |
| Flatpak / Flathub | Manifest that survives review, `com.pynsource.Pynsource` app id | deferred: a release-page `.flatpak` is close to useless, and the AppImage already covers Linux |
| Community canvas | Decide whether Community keeps `src/ogl` or moves to `wxdiagram` | after 2.0 |

## Watch-outs

- **One version number, several files.** `tbump.toml` patches `src/gui/settings.py`,
  `.requirement-extras/buildwin_github-actions.iss` and `DOWNLOADS.md`; `CHANGELOG.md`,
  `Admin/site-atug/pynsource-latest{-devel,}.txt` are by hand.
- **Tags are stable releases, `pre-*` tags are drafts.** Existing 1.x licences keep working
  because licensing keys off `APP_VERSION` with a forward window; never jump to 2.x casually.
- **A release body only sticks to a brand-new draft** (`action-gh-release` will not re-body an
  existing draft), so notes changes need a new tag or a deleted draft.
- **Snap stable is promoted by hand** in the store UI after installing and running the build.
- **Pro is free on Linux by platform**, so every Linux artefact must bundle `ogl2` (and `alsm`
  for module visualisation). macOS/Windows CI never exercises those imports.
