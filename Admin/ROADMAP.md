# Pynsource roadmap and release status

Current stable: **1.86** (November 2026). Next: **1.87**, the wxdiagram canvas release. Previous stable: 1.84 (2022); 1.85 was a beta series.

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

1. ~~Promote the snap to `stable`~~ — done 2026-11-16: rev 34 (amd64) and 35 (arm64) are on
   `latest/stable`, and the "edge while being tested" wording is gone from README/DOWNLOADS.
2. Sanity-check zoom speed on bare metal (mac + a real Linux desktop). A GPU-less VM is the
   worst case for a `PaintDC` canvas and is not evidence of a regression.
3. Optional tidy: delete the old `pre-*` releases except the most recent.

## The canvas: wxdiagram

Pynsource has **one canvas on every platform and edition**: `wxdiagram` (MIT), driven by
`src/gui/uml_canvas.py`. The old choices are gone:

| Edition | Canvas | Where it lives |
|---|---|---|
| Community | `wxdiagram` | separate repo `abulka/wxdiagram` |
| Pro / Linux | `wxdiagram` | same |

The vendored classic OGL copy (`src/ogl/`) and the `ogl2` sibling are no longer used. The
PyInstaller spec, mac/win build scripts and `.icns` icon now live in this repo (`bin/`,
`src/media/`), so a build change no longer needs a push to another repo.

The diagram is free: zoom, pan, pinch, drag-to-connect, resize and layout are not gated.
`wxdiagram` owns the viewport (zoom, Ctrl+wheel, pinch, drag-to-pan, virtual size); pynsource
keeps only `coordmapper` for layout/world coordinates. `PRO_EDITION` only gates **module
visualisation** (ALSM) on macOS/Windows; it is free on Linux builds.

## Milestones

| Milestone | Content | Notes |
|---|---|---|
| 1.86 | First stable release since 1.84; all platforms built by CI | published |
| 1.87 | One canvas (`wxdiagram`); diagram free; Pro = ALSM only | in progress |
| 1.87.x | Patch releases via `PATCH` in `src/gui/settings.py` | no retagging |
| wxdiagram 0.2 | Integration hooks (`MoveTo`, `getContentBounds`, opt-out flags) | own repo/release |
| Flatpak / Flathub | Manifest that survives review, `com.pynsource.Pynsource` app id | deferred: a release-page `.flatpak` is close to useless, and the AppImage already covers Linux |

## Watch-outs

- **One version number, several files.** `tbump.toml` patches `src/gui/settings.py`,
  `.requirement-extras/buildwin_github-actions.iss` and `DOWNLOADS.md`; `CHANGELOG.md`,
  `Admin/site-atug/pynsource-latest{-devel,}.txt` are by hand.
- **Tags are stable releases, `pre-*` tags are drafts.** Existing 1.x licences keep working
  because licensing keys off `APP_VERSION` with a forward window; never jump to 2.x casually.
- **A release body only sticks to a brand-new draft** (`action-gh-release` will not re-body an
  existing draft), so notes changes need a new tag or a deleted draft.
- **Snap stable is promoted by hand** in the store UI after installing and running the build.
- **No URL shortener.** The in-app update check reads `Admin/site-atug/pynsource-latest.txt`
  straight from `raw.githubusercontent.com`, and the website links directly at release assets.
  bit.ly's free plan is gone and its links rotted (one pointed at a two-year-old download page),
  so nothing new should use it. Caveat: the update-check URL is compiled into each binary, so
  only releases from 1.87 onward are free of the old short links.
- **macOS is Apple silicon only, by decision.** Intel Macs stop at 1.84. The tooling would allow
  an Intel build (`macos-15-intel` plus the existing x86_64 wxPython wheels), but GitHub retires
  its Intel runners in August 2027 and macOS 26 is the last Intel macOS - not worth building a
  path with a fixed expiry date.
- **Pro is free on Linux by platform**, so every Linux artefact must bundle `wxdiagram` and
  `alsm`.
