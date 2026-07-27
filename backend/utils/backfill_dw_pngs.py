"""
backfill_dw_pngs.py

GeoSentinel AI — One-time backfill utility.

Scans all analysis_results rows where dynamic_world_before_path or
dynamic_world_after_path points to a .tif file, generates colorized
PNGs, and updates the DB to point to the PNGs instead.

Run once:
    python -m backend.utils.backfill_dw_pngs
"""

import sqlite3
import sys
from pathlib import Path

# Adjust path so the project root is on sys.path
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.models.dynamic_world_colorizer import colorize_dynamic_world

DB_NAME = ROOT / "backend" / "database" / "geosentinel.db"


def _tif_to_png_path(tif_path: str) -> str:
    """
    Return the expected PNG path for a DW TIF.
    e.g. .../dynamic_world/before_dynamic_world.tif
      → .../dynamic_world/before_dynamic_world.png
    """
    p = Path(tif_path)
    return str(p.with_suffix(".png"))


def backfill(dry_run: bool = False) -> None:
    print("=" * 70)
    print("GeoSentinel AI — Dynamic World PNG Backfill")
    print("=" * 70)

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, aoi_id,
               dynamic_world_before_path,
               dynamic_world_after_path
        FROM analysis_results
        ORDER BY id
        """
    )
    rows = cur.fetchall()
    print(f"\nTotal rows: {len(rows)}")

    updated = 0
    skipped = 0
    failed = 0

    for row in rows:
        row_id = row["id"]
        aoi_id = row["aoi_id"]
        before_path = row["dynamic_world_before_path"]
        after_path = row["dynamic_world_after_path"]

        print(f"\n--- id={row_id} aoi={aoi_id} ---")

        new_before = None
        new_after = None

        # ---- Before ----
        if before_path and before_path.endswith(".tif"):
            png_path = _tif_to_png_path(before_path)
            existing_png = Path(png_path)
            if existing_png.exists():
                print(f"  [before] PNG already exists: {existing_png.name}")
                new_before = png_path
            elif Path(before_path).exists():
                print(f"  [before] Colorizing {Path(before_path).name}...")
                if not dry_run:
                    result = colorize_dynamic_world(before_path, png_path)
                    if result:
                        new_before = result
                        print(f"  [before] Generated: {Path(result).name}")
                    else:
                        print(f"  [before] FAILED to generate PNG")
                        failed += 1
                else:
                    print(f"  [before] DRY RUN — would generate {Path(png_path).name}")
                    new_before = png_path
            else:
                print(f"  [before] TIF not found on disk — skipping")
                skipped += 1
        elif before_path and before_path.endswith(".png"):
            print(f"  [before] Already PNG: {Path(before_path).name}")
            new_before = before_path
        else:
            print(f"  [before] No path or null — skipping")
            skipped += 1

        # ---- After ----
        if after_path and after_path.endswith(".tif"):
            png_path = _tif_to_png_path(after_path)
            existing_png = Path(png_path)
            if existing_png.exists():
                print(f"  [after]  PNG already exists: {existing_png.name}")
                new_after = png_path
            elif Path(after_path).exists():
                print(f"  [after]  Colorizing {Path(after_path).name}...")
                if not dry_run:
                    result = colorize_dynamic_world(after_path, png_path)
                    if result:
                        new_after = result
                        print(f"  [after]  Generated: {Path(result).name}")
                    else:
                        print(f"  [after]  FAILED to generate PNG")
                        failed += 1
                else:
                    print(f"  [after]  DRY RUN — would generate {Path(png_path).name}")
                    new_after = png_path
            else:
                print(f"  [after]  TIF not found on disk — skipping")
                skipped += 1
        elif after_path and after_path.endswith(".png"):
            print(f"  [after]  Already PNG: {Path(after_path).name}")
            new_after = after_path
        else:
            print(f"  [after]  No path or null — skipping")
            skipped += 1

        # ---- Update DB ----
        if not dry_run and (new_before or new_after):
            cur.execute(
                """
                UPDATE analysis_results
                SET dynamic_world_before_path = COALESCE(?, dynamic_world_before_path),
                    dynamic_world_after_path  = COALESCE(?, dynamic_world_after_path)
                WHERE id = ?
                """,
                (new_before, new_after, row_id),
            )
            updated += 1

    if not dry_run:
        conn.commit()
        print(f"\n✓ Committed {updated} DB updates")
    else:
        print(f"\nDRY RUN complete — {updated} rows would be updated")

    conn.close()

    print(f"\nSummary:")
    print(f"  Updated : {updated}")
    print(f"  Skipped : {skipped}")
    print(f"  Failed  : {failed}")
    print("=" * 70)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Backfill Dynamic World colorized PNGs in SQLite."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without writing to DB.",
    )
    args = parser.parse_args()

    backfill(dry_run=args.dry_run)
