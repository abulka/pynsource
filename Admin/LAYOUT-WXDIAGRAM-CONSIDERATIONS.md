# pynsource layout vs wxdiagram layout

**Status:** analysis and decision record (2026-11-18)

Yes — and in one sense the extraction has already happened. `wxdiagram/layout_spring.py` is the newer, deterministic, node-size-aware version of pynsource’s 186-line `GraphLayoutSpring`, with extra refinement/metrics modules. What’s left is switching pynsource to consume it and deleting the old kernel.

But you’re right to be careful. The **force kernel** is duplicated; the **layout pipeline around it** is not. Pynsource still owns the coordinate mapper, overlap remover, snapshots/blackboard, expand/contract, and deep-layout animation. Ripping out the file without replacing those contracts would break the UX.

## Recommended approach

Keep `pynsource/src/layout/layout_spring.py` as a thin compatibility adapter, not delete it outright:

1. `GraphLayoutSpring(graph, gui=None)` stays.
2. Convert `graph.nodes` / `graph.edges` into `LayoutNode` / `LayoutEdge`.
3. Call `wxdiagram.layout_spring.SpringLayout`.
4. Copy results back into `node.layoutPosX/layoutPosY`.
5. Update `graph.layoutMinX/MaxX/MinY/MaxY`, then let the existing `CoordinateMapper` → `OverlapRemoval` pipeline run unchanged.
6. Keep `layout(keep_current_positions=False, optimise=True)` returning `None`, plus existing attributes (`iterations`, `k`, `c`, `maxVertexMovement`) for compatibility.

That gets one implementation of the algorithm with a minimal blast radius. Pynsource’s richer overlap removal and scale/expand behaviour stay authoritative for now.

## The important gotchas

- **Different coordinate contract.** Pynsource’s spring writes dimensionless `layoutPosX/Y`; `CoordinateMapper` turns those into world pixels and supports the expand/contract commands. wxdiagram returns absolute top-left pixel positions with margins, component packing, sizing and overlap separation. Decide deliberately whether to treat wxdiagram’s output *as* pynsource layout coordinates (simplest) or add a “raw force space” output mode.
- **Bounds semantics.** If you map wxdiagram results into pynsource layout space, compute `layoutMin/Max` from the **top-left positions**, like the old `layoutCalcBounds()`, not from `LayoutResult.bounds` (which includes node widths/heights). Otherwise the coordinate mapper scales things differently.
- **Layouts will look different.** Old: all nodes start at `(0,0)` with random jitter, 1500 iterations. New: deterministic sorted grid start, 500 iterations with early stop, size-aware spacing, component packing and crossing refinement. There are no golden-position tests, but screenshots and user expectations will change.
- **Deep layout’s “best of N” may break.** The seed currently only affects coincident-node jitter, so with a grid start every attempt would be identical. `LayoutMultipleChooseBest` would waste time comparing identical layouts. We likely need a `random_start`/jitter option, or vary initial positions per attempt.
- **Don’t double-handle overlaps.** wxdiagram already runs `_separate_overlaps` and `_pack_components`; pynsource then runs its much stronger `OverlapRemoval`, which also handles line–node crossings. Choose one owner. My preference: keep pynsource’s overlap remover as the final authority, and add/use options to skip or tolerate wxdiagram’s separation when running under pynsource.
- **Blackboard metrics will change.** `GetVitalStats` uses pynsource’s LL/LN/NN counts and pre-overlap NN count. If wxdiagram removes overlaps before pynsource measures them, those numbers (and the snapshot scoring) change. Some strategies may look like they have nothing to do.
- **Edge semantics differ.** wxdiagram deduplicates edges by `(source, target, weight)` and skips self-loops; pynsource applies attraction per edge and keys duplicates by UML edge type. It also defaults missing/under-1 weights to 1. Decide whether pynsource should preserve per-edge duplication and side effects.
- **Cancellation and progress.** Pynsource uses `gui.kill_layout` and repaints every 100 iterations. The adapter should translate that to wxdiagram’s `on_step` returning `False`, with throttled `mega_refresh` calls. Keep it thread-safe: wxdiagram itself is pure and safe in the worker thread.
- **Fixed nodes / keep positions.** Pynsource has no fixed-node concept and always calls `keep_current_positions=False`. Don’t accidentally map current shape positions into `keep_positions=True`.
- **Packaging/import details.** Use a direct `from wxdiagram.layout_spring import SpringLayout`; be aware that importing a wxdiagram submodule still executes `wxdiagram/__init__.py`, which imports `wx`. Pynsource already depends on wx, so this is fine, but pure/headless layout tests would need wx installed.
- **Version/release sequencing.** Pynsource currently pins `wxdiagram>=0.2.1,<0.3`. If the adapter needs new options, release a wxdiagram patch first, then bump pynsource’s lower bound. CI already installs wxdiagram editable from `main`, but PyPI installs and builds need the release ordering.
- **Licensing/attribution.** wxdiagram is MIT and pynsource is GPL3. Because the wxdiagram version already exists, consuming it from pynsource is fine. Just avoid literally copying pynsource GPL code into the MIT package; keep the provenance note accurate.

## Suggested sequence

1. **Baseline:** run pynsource’s suite (`bin/testall`, or targeted unittest modules), capture before/after screenshots and LL/LN/overlap/bitmap timing for a small, medium and large graph.
2. **Adapter only:** no wxdiagram changes. Treat wxdiagram positions as pynsource layout coordinates; keep `CoordinateMapper` and `OverlapRemoval`; keep public API.
3. **Evaluate:** check layout quality, overlap-removal behaviour, deep-layout variation, cancellation and expand/contract.
4. **Only then add wxdiagram options** if needed: random start/seed variation, `separate_overlaps`/`pack_components` toggles, or a raw-layout output mode.
5. **Cleanup:** update docs/architecture notes, remove genuinely dead pynsource code, keep the adapter for one release.

My vote is to do step 1–3 first with **no new wxdiagram API**, because the force kernel swap is clean and reversible. The main decision to settle before coding is: *does pynsource keep its coordinate mapper and overlap remover as the layout pipeline owner, or do we migrate those too?* I’d keep them for now — otherwise this stops being a duplicate removal and becomes a layout-system rewrite.

## Decision (2026-11-18): leave the engines separate

We are **not** swapping pynsource onto `wxdiagram.SpringLayout` at this time.
Keeping the two implementations is the better trade-off today.  The label to
use is "an intentional application/library boundary", not "unfinished
deduplication".

### Why

- **They are no longer true duplicates.**  Pynsource starts every node at
  `(0, 0)` with random jitter and runs 1500 iterations.  wxdiagram starts on a
  sorted grid, runs 500 iterations with early stopping, uses node sizes,
  packs components and refines crossings.  They are forked behaviours with
  different visual results.
- **The duplicated surface is small and stable.**  Pynsource's engine is 186
  lines that has not needed changes since 2023.  An adapter would save roughly
  100 lines, but would also add conversion code, option plumbing and visual
  tuning.  The net maintenance saving is modest.
- **The surrounding pipeline is not duplicated.**  `CoordinateMapper`,
  `OverlapRemoval`, snapshots and `LayoutBlackboard` are pynsource-specific.
  Swapping the kernel forces a decision about those too, and the sensible
  answer (migrate them as well) turns this into a layout-system rewrite.
- **Layout quality is subjective and user-visible.**  Tests can prove that
  nodes do not overlap and edges still connect, but they cannot prove that the
  new diagrams look as good.  Changing the layout users see is a product risk,
  not just a refactor.
- **Deep layout would regress unless more work is done.**  wxdiagram's seed
  currently only affects coincident-node jitter.  With a deterministic grid
  start, all "best of N" attempts would be identical, so pynsource would need
  a new random-start/jitter option in wxdiagram.
- **Pure layout tests are worth keeping.**  `import wxdiagram.layout_spring`
  still executes `wxdiagram/__init__.py`, which imports `wx`.  Pynsource
  already depends on wx, so CI would pass, but the layout modules currently
  have a nice no-wx property.  Preserving that would require making the
  wxdiagram package lazy or splitting the pure layout code into a separate
  distribution — extra scope.

### What the adapter would have bought

For the record, the recommended adapter was technically sound:

- one spring force kernel to maintain;
- pynsource's `layout_spring.py` reduced to a compatibility wrapper;
- existing coordinate mapping, overlap removal, expand/contract and deep
  layout preserved;
- no changes needed in wxdiagram.

It would not have removed the conceptual overlap between the two *pipelines*
(layout space vs. size-aware pixel placement, simple vs. rich overlap removal),
so it would not have produced a clean single implementation either.

### What we do instead

- Freeze pynsource's engine as the application-specific layout pipeline and
  add a header comment explaining the boundary (done).
- Keep wxdiagram's `SpringLayout` as the library's generic, deterministic,
  node-size-aware engine.  It is not expected to reproduce pynsource's output.
- Treat wxdiagram's layout docs appendix as the public record of the heritage
  and the differences.
- Revisit only when there is a concrete reason: a layout bug that must be
  fixed in both engines, a new layout feature pynsource wants, a major UI
  change where a visual layout change is acceptable, or a quiet release window
  with time for a proper before/after comparison.

### If the swap is ever attempted

Do it as a time-boxed spike on a branch.  Merge only if all of these hold:

- pynsource's `bin/testall` and overlap stress tests pass;
- before/after screenshots on several real diagrams look as good or better;
- deep layout still produces distinct candidate layouts;
- ESC/cancel stays responsive during layout;
- expand/contract and snapshot restore still work;
- no new pynsource-specific options are required in wxdiagram.

Otherwise delete the branch and keep this decision.

