import pya
from collections import Counter
from pathlib import Path

def print_hierarchy(cell, layout, depth=0, max_depth=5):
    indent = "    " * depth

    print(
        f"{indent}└─ {cell.name}"
        f"  [bbox={cell.bbox()}, "
        f"instances={cell.child_instances()}]"
    )

    if depth >= max_depth:
        return

    for inst in cell.each_inst():
        child = inst.cell

        print(
            f"{indent}   "
            f"↳ {child.name}"
            f"  trans={inst.trans}"
            f"  bbox={inst.bbox()}"
        )

        if child.child_instances() > 0:
            print_hierarchy(
                child,
                layout,
                depth + 1,
                max_depth
            )

# ============================================================
# Configuration
# ============================================================

gdsfile = "04_final.gds"

# ============================================================
# Helpers
# ============================================================

def fmt_point(p):
    return f"({p.x:>8}, {p.y:>8})"


def fmt_bbox(b):
    return (
        f"({b.left:>8},{b.bottom:>8})"
        f" → "
        f"({b.right:>8},{b.top:>8})"
    )


def fmt_trans(t):
    return f"{t.disp} / {t.angle}° / mirror={t.is_mirror()}"


def cell_stats(cell):
    return {
        "instances": cell.child_instances(),
        "bbox": cell.bbox(),
        "width": cell.bbox().width(),
        "height": cell.bbox().height(),
    }


# ============================================================
# Load
# ============================================================

layout = pya.Layout()
layout.read(gdsfile)

top = layout.top_cell()

# ============================================================
# Header
# ============================================================

print()
print("=" * 120)
print(" GDSII DESIGN INSPECTOR")
print("=" * 120)

print(f"File       : {Path(gdsfile).resolve()}")
print(f"Top cell   : {top.name}")
print(f"Database μm: {layout.dbu}")
print(f"Cell count : {layout.cells()}")
print()

# ============================================================
# Top-level instances
# ============================================================

instances = list(top.each_inst())

print("-" * 120)
print(f" TOP-LEVEL INSTANCES ({len(instances)})")
print("-" * 120)

header = (
    f"{'#':>4}  "
    f"{'CELL':<42} "
    f"{'ORIGIN':<22} "
    f"{'BBOX':<42} "
    f"{'SIZE':<22}"
)

print(header)
print("-" * 120)

cell_counts = Counter()

for i, inst in enumerate(instances):
    cell = inst.cell
    bbox = inst.bbox()

    cell_counts[cell.name] += 1

    size = f"{bbox.width()} × {bbox.height()}"

    print(
        f"{i:>4}  "
        f"{cell.name:<42} "
        f"{fmt_point(inst.trans.disp):<22} "
        f"{fmt_bbox(bbox):<42} "
        f"{size:<22}"
    )

print_hierarchy(top, layout)
# ============================================================
# Orientation / transformation report
# ============================================================

print()
print("-" * 120)
print(" TRANSFORMATIONS")
print("-" * 120)

for i, inst in enumerate(instances):
    print(
        f"{i:>4}  "
        f"{inst.cell.name:<42} "
        f"{fmt_trans(inst.trans)}"
    )

# ============================================================
# Cell frequency summary
# ============================================================

print()
print("-" * 120)
print(" CELL TYPE SUMMARY")
print("-" * 120)

print(f"{'COUNT':>8}  {'CELL TYPE':<60}")
print("-" * 120)

for cell_name, count in cell_counts.most_common():
    print(f"{count:>8}  {cell_name:<60}")


# ============================================================
# Layer Usage
# ============================================================
print()
print("-" * 100)
print(" LAYER USAGE")
print("-" * 100)

for layer_index in range(layout.layers()):
    info = layout.get_info(layer_index)

    count = 0

    for cell in layout.each_cell():
        count += cell.shapes(layer_index).size()

    if count:
        print(
            f"Layer {layer_index:>3}  "
            f"({info.layer:>3}/{info.datatype:<3})  "
            f"{info.name:<35} "
            f"shapes={count}"
        )

# ============================================================
# Top-cell geometry
# ============================================================

print()
print("-" * 120)
print(" TOP CELL GEOMETRY")
print("-" * 120)

bbox = top.bbox()

print(f"Bounding box : {fmt_bbox(bbox)}")
print(f"Width        : {bbox.width()}")
print(f"Height       : {bbox.height()}")
print(f"Area         : {bbox.width() * bbox.height()}")
print(f"Center       : {fmt_point(bbox.center())}")

print()
print("=" * 120)
print(" END REPORT")
print("=" * 120)
