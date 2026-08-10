#!/usr/bin/env python3

import pya
import json
import sys
from collections import Counter
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

GDSFILE = "04_final.gds"
OUTPUT_JSON = "logical_cells.json"

LOGICAL_PREFIX = "sky130_fd_sc_hd__"

# Physical-only cells observed in the GDS inventory.
PHYSICAL_ONLY = {
    "sky130_fd_sc_hd__decap_3",
    "sky130_fd_sc_hd__tapvpwrvgnd_1",
}

# Additional non-standard-cell structures seen in the design.
# These are intentionally excluded from the logical-cell database.
NON_LOGICAL_PREFIXES = (
    "VIA_",
)

# ============================================================
# Helpers
# ============================================================

def point_dict(p):
    return {
        "x": p.x,
        "y": p.y,
    }


def bbox_dict(b):
    return {
        "left": b.left,
        "bottom": b.bottom,
        "right": b.right,
        "top": b.top,
        "width": b.width(),
        "height": b.height(),
    }


def trans_dict(t):
    return {
        "x": t.disp.x,
        "y": t.disp.y,
        "angle": t.angle,
        "mirror": t.is_mirror(),
        "str": str(t),
    }


def is_logical_cell(cell_name):
    """
    Determine whether a cell should be treated as a logical
    standard-cell instance.

    This is deliberately conservative: only SKY130 HD cells
    are accepted, and known physical-only structures are removed.
    """

    if not cell_name.startswith(LOGICAL_PREFIX):
        return False

    if cell_name in PHYSICAL_ONLY:
        return False

    for prefix in NON_LOGICAL_PREFIXES:
        if cell_name.startswith(prefix):
            return False

    return True


# ============================================================
# Load GDS
# ============================================================

print()
print("=" * 100)
print(" SKY130 LOGICAL CELL EXTRACTOR")
print("=" * 100)

print(f"GDS file : {GDSFILE}")

layout = pya.Layout()
layout.read(GDSFILE)

top = layout.top_cell()

print(f"Top cell : {top.name}")
print(f"DBU      : {layout.dbu}")
print(f"Cells    : {layout.cells()}")
print()


# ============================================================
# Extract logical instances
# ============================================================

logical_cells = []
excluded_cells = []

logical_counts = Counter()
excluded_counts = Counter()

instance_number = 0


for inst in top.each_inst():

    cell = inst.cell
    cell_name = cell.name

    record = {
        "id": instance_number,
        "master": cell_name,
        "cell_index": cell.cell_index(),
        "origin": point_dict(inst.trans.disp),
        "transform": trans_dict(inst.trans),
        "bbox": bbox_dict(inst.bbox()),
    }

    if is_logical_cell(cell_name):

        logical_cells.append(record)
        logical_counts[cell_name] += 1

    else:

        excluded_cells.append(record)
        excluded_counts[cell_name] += 1

    instance_number += 1


# ============================================================
# Print logical-cell report
# ============================================================

print("-" * 100)
print(
    f" LOGICAL STANDARD CELLS "
    f"({len(logical_cells)} instances)"
)
print("-" * 100)

print(
    f"{'ID':>5}  "
    f"{'MASTER':<40} "
    f"{'ORIGIN':<20} "
    f"{'ORIENTATION':<20}"
)

print("-" * 100)

for cell in logical_cells:

    origin = (
        f"({cell['origin']['x']}, "
        f"{cell['origin']['y']})"
    )

    transform = cell["transform"]

    orientation = (
        f"{transform['angle']}°"
        f"{' MIRROR' if transform['mirror'] else ''}"
    )

    print(
        f"{cell['id']:>5}  "
        f"{cell['master']:<40} "
        f"{origin:<20} "
        f"{orientation:<20}"
    )


# ============================================================
# Logical cell type summary
# ============================================================

print()
print("-" * 100)
print(" LOGICAL CELL TYPE SUMMARY")
print("-" * 100)

print(
    f"{'COUNT':>8}  "
    f"{'CELL MASTER':<70}"
)

print("-" * 100)

for cell_name, count in logical_counts.most_common():

    print(
        f"{count:>8}  "
        f"{cell_name:<70}"
    )


# ============================================================
# Excluded-cell summary
# ============================================================

print()
print("-" * 100)
print(" EXCLUDED / NON-LOGICAL CELL SUMMARY")
print("-" * 100)

print(
    f"{'COUNT':>8}  "
    f"{'CELL':<70}"
)

print("-" * 100)

for cell_name, count in excluded_counts.most_common():

    print(
        f"{count:>8}  "
        f"{cell_name:<70}"
    )


# ============================================================
# Write JSON database
# ============================================================

database = {
    "metadata": {
        "source_gds": str(Path(GDSFILE).resolve()),
        "top_cell": top.name,
        "dbu": layout.dbu,
        "total_top_level_instances": instance_number,
        "logical_instance_count": len(logical_cells),
        "excluded_instance_count": len(excluded_cells),
    },

    "cell_types": {
        cell_name: {
            "count": count
        }
        for cell_name, count in logical_counts.items()
    },

    "instances": logical_cells,

    "excluded_instances": excluded_cells,
}


with open(OUTPUT_JSON, "w") as f:
    json.dump(database, f, indent=2)


# ============================================================
# Final summary
# ============================================================

print()
print("=" * 100)
print(" EXTRACTION COMPLETE")
print("=" * 100)

print(
    f"Total top-level instances : {instance_number}"
)

print(
    f"Logical instances         : {len(logical_cells)}"
)

print(
    f"Excluded instances        : {len(excluded_cells)}"
)

print(
    f"Logical cell types        : {len(logical_counts)}"
)

print(
    f"JSON output               : {OUTPUT_JSON}"
)

print("=" * 100)
