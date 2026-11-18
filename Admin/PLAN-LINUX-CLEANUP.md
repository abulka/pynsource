# PLAN: Linux / snap packaging cleanup (deferred)

**Status: NOT STARTED ON PURPOSE (2026-11-18).** The Linux AppImage and snap both build only in
CI, and they work right now. Do not start this cleanup while a release is in flight: every change
here is only observable by dispatching a workflow, so a mistake shows up as a broken release
artefact rather than a failing local test.

Written down so a future session does not have to rediscover it, and does not "helpfully" delete
files that CI still needs.

---

## 1. What was already changed (safe, no CI impact)

* `.requirement-extras/requirements-linux-22.txt` — **deleted**. It was the 2020-era "compile
  wxPython from source on Ubuntu" recipe (EOL `libwebkit2gtk-4.0-dev` etc. in its header) and had
  exactly one reader: `setup.py`. Nothing in CI or the snap used it.
* `setup.py` — now reads `requirements.txt` for `install_requires` and scrapes `APP_VERSION` from
  `src/gui/settings.py`. Before this, the sdist claimed `py2app` (mac-only) as a runtime
  dependency and `uv build` produced `pynsource-1.0.0.tar.gz` while the app was 1.87.
* `requirements.txt` — `pydbg` removed (a Rust-built debugger whose imports are all commented out
  in `src/`; it was the slowest part of a cold `bin/boot`).
* `bin/` — old author-specific scripts removed, `bin/boot` added; see `bin/README.md`.

None of that touches the snap: it installs from `.requirement-extras/requirements-snap.txt`, not
from `requirements.txt`.

## 2. The actual problem: the snap ships the test/dev set

`snap/snapcraft.yaml` does one `pip install --target` per arch:

```
/usr/bin/python3 -m pip install --target "$SITE" --no-warn-script-location \
  -r .requirement-extras/requirements-snap.txt "$WX"
```

and `requirements-snap.txt` is nothing but:

```
-r requirements-linux-common.txt
wxasync
```

`requirements-linux-common.txt` contains `configobj requests astpretty termcolor beautifultable
appdirs wheel pydbg aiohttp async_lru Pillow py2app click pytest coverage pytest-cov black`
(`pydbg` was removed from `requirements.txt` in this change but **not** in this file). So the
shipped snap installs pytest, coverage, black, and mac-only py2app into
`$SNAP/usr/lib/python3.12/site-packages` — several MB of dead weight (pytest, black and coverage
are the bulk) plus `py2app` in a Linux package that can never use it.

### Proposed fix

1. Rewrite `.requirement-extras/requirements-snap.txt` as a self-contained, runtime-only list.
   The runtime third-party imports gathered from `src/` are: `configobj`, `requests`, `astpretty`,
   `termcolor`, `beautifultable`, `appdirs`, `aiohttp`, `async_lru`, `Pillow`, `click`, `wxasync`.
   (`ast`/`json`/etc. are stdlib; `wxdiagram` and `alsm` are installed separately by `snapcraft.yaml`
   from the sibling checkouts, and wxPython is the `"$WX"` argument.)
2. Delete `.requirement-extras/requirements-linux-common.txt` (its only remaining readers are
   `requirements-snap.txt` and the dead `snap/local/snapcraft-18.04.yaml`).
3. Fix the now-false comment in `snap/snapcraft.yaml` above the pip line: it says
   "requirements-linux-common.txt contains a bare `wxpython` line", and it no longer does (check
   before editing — `requirements-snap.txt` may need the same note). The one-pip-invocation
   requirement is still real, but for a different reason: a `--target` install is invisible to a
   later pip run, so splitting the wx wheel from the requirement list makes pip rebuild wx from
   source.

### Verification (all of it is CI-only)

```bash
gh workflow run build-snap.yml            # artifact only on a branch; edge upload on a tag
# then, from the downloaded .snap artifact on an Ubuntu box:
snap install --dangerous pynsource_*.snap
snap run pynsource.pynsource-cli --version     # prints the version; asserts alsm importable
# and confirm the bloat is gone:
ls $SNAP/usr/lib/python3.12/site-packages | grep -E 'pytest|black|py2app'   # expect nothing
```

Also re-check that the app still starts, under xvfb if headless, using the same guard the
workflow uses (it asserts `AppRun`/launcher is alive after 25 s and that the log does **not** say
"Running Community Edition" — Linux must come up Pro).

## 3. Dead snap leftovers

`snap/local/snapcraft-18.04.yaml` — `base: core18`, EOL since 2023, and nothing references it
(the workflow packs `snap/snapcraft.yaml`, which is `core24`). Its only unique input is
`snap/local/andy-diagnostics/report_snap_env.py`, referenced by that file alone. Delete both in
the same commit as section 2, after the snap build has been proven once.

## 4. Do not delete `setup.py` yet

It looks vestigial (no PyPI publishing, `pip install pynsource` is not advertised anywhere), but
the snap still runs `pip install --target "$SITE" --no-deps .`, which executes `setup.py`. Deleting
it needs a `pyproject.toml` build backend first, and that is a separate, larger piece of work:

* `pyproject.toml` would let `uv sync` + `uv run` replace `bin/boot` / `bin/run` / `bin/testall`;
* `[dependency-groups] dev = [...]` would separate runtime from test deps, which also fixes the
  sdist metadata (right now `install_requires` is `requirements.txt` verbatim, so pytest and
  coverage are declared as install dependencies);
* editable siblings would move to `[tool.uv.sources]` (`path = "../wxdiagram"`), which breaks
  plain clones with no siblings — the reason `bin/boot` still exists as the documented escape
  hatch.

Until then: `setup.py` stays, `requirements.txt` stays the single source of truth for the venv.

## 5. Housekeeping note for local venvs

pip never prunes. An existing `.venv` keeps `pydbg` (and any `py2app`) after the
`requirements.txt` change:

```bash
uv pip uninstall pydbg py2app
```

`bin/boot` deliberately does not remove packages.
