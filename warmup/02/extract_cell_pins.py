#!/usr/bin/env python3

import pya
import json
import sys
from collections import defaultdict, Counter
from pathlib import Path


# ============================================================
# Configuration
# ============================================================

GDSFILE = "04_final.gds"
INPUT_JSON = "logical_cells.json"
OUTPUT_JSON = "cell_pins.json"

# Only inspect logical SKY130 cells
LOGICAL_PREFIX = "sky130_fd_sc_hd__"

# Text labels which are obviously not logical pin names.
# This is deliberately conservative.
IGNORED_LABELS = {
    "",
    "VDD",
    "VSS",
    "VPWR",
    "VGND",
    "VPB",
    "VNB",
}

# Common power-related names which we record separately.
POWER_NAMES = {
    "VDD",
    "VSS",
    "VPWR",
    "VGND",
    "VPB",
    "VNB",
    "VCCD",
    "VSSD",
}


# ============================================================
# Helpers
# ============================================================

def point_dict(p):
    return {
        "x": int(p.x),
        "y": int(p.y),
    }


def trans_dict(t):
    return {
        "x": int(t.disp.x),
        "y": int(t.disp.y),
        "angle": int(t.angle),
        "mirror": bool(t.is_mirror()),
        "str": str(t),
    }


def bbox_dict(b):
    return {
        "left": int(b.left),
        "bottom": int(b.bottom),
        "right": int(b.right),
        "top": int(b.top),
        "width": int(b.width()),
        "height": int(b.height()),
    }


def shape_bbox(shape):
    """
    Return a bbox for a KLayout shape.

    Text shapes do not necessarily have a useful geometric bbox
    for our purposes, so text_pos is used separately.
    """
    try:
        b = shape.bbox()
        return bbox_dict(b)
    except Exception:
        return None


def is_power_label(name):
    return name.upper() in POWER_NAMES


# ============================================================
# Load input database
# ============================================================

print()
print("=" * 110)
print(" SKY130 CELL PIN EXTRACTOR")
print("=" * 110)

print(f"GDS       : {GDSFILE}")
print(f"Input DB  : {INPUT_JSON}")
print(f"Output DB : {OUTPUT_JSON}")
print()


with open(INPUT_JSON, "r") as f:
    logical_db = json.load(f)


layout = pya.Layout()
layout.read(GDSFILE)

print(f"Top cell  : {layout.top_cell().name}")
print(f"DBU       : {layout.dbu}")
print(f"GDS cells : {layout.cells()}")
print()


# ============================================================
# Determine which master cells we actually need
# ============================================================

master_names = sorted(
    logical_db["cell_types"].keys()
)

print("-" * 110)
print(" LOGICAL CELL MASTERS")
print("-" * 110)

for name in master_names:
    count = logical_db["cell_types"][name]["count"]
    print(f"{count:>5} × {name}")

print()


# ============================================================
# Extract text labels from each master
# ============================================================

master_pin_data = {}

total_text_labels = 0
total_candidate_pins = 0


for master_name in master_names:

    print("-" * 110)
    print(f" MASTER: {master_name}")
    print("-" * 110)

    # --------------------------------------------------------
    # Find master cell
    # --------------------------------------------------------

    cell = None

    for ci in range(layout.cells()):
        candidate = layout.cell(ci)

        if candidate is not None and candidate.name == master_name:
            cell = candidate
            break

    if cell is None:

        print("  ERROR: master cell not found in GDS")
        master_pin_data[master_name] = {
            "error": "master cell not found",
            "pins": [],
        }
        continue

    print(f"  Cell index : {cell.cell_index()}")
    print(f"  BBox       : {cell.bbox()}")
    print(
        f"  Size       : "
        f"{cell.bbox().width()} × "
        f"{cell.bbox().height()}"
    )

    # --------------------------------------------------------
    # Extract text labels
    # --------------------------------------------------------

    labels = []
    layers_seen = Counter()

    for layer_index in range(layout.layers()):

        shapes = cell.shapes(layer_index)

        for shape in shapes.each():

            if not shape.is_text():
                continue

            try:
                text = shape.text_string
            except Exception:
                try:
                    text = shape.text
                except Exception:
                    continue

            if text is None:
                continue

            text = str(text).strip()

            if not text:
                continue

            info = layout.get_info(layer_index)

            try:
                pos = shape.text_pos
                pos_dict = point_dict(pos)
            except Exception:
                pos_dict = None

            try:
                dpos = shape.text_dpos
                dpos_dict = {
                    "x_um": float(dpos.x),
                    "y_um": float(dpos.y),
                }
            except Exception:
                dpos_dict = None

            try:
                text_trans = shape.text_trans
                text_trans_dict = trans_dict(text_trans)
            except Exception:
                text_trans_dict = None

            label = {
                "text": text,
                "layer_index": layer_index,
                "layer": int(info.layer),
                "datatype": int(info.datatype),
                "layer_name": info.name,
                "position": pos_dict,
                "position_um": dpos_dict,
                "transform": text_trans_dict,
                "bbox": shape_bbox(shape),
                "is_power": is_power_label(text),
            }

            labels.append(label)
            layers_seen[
                f"{info.layer}/{info.datatype}"
            ] += 1

    total_text_labels += len(labels)

    # --------------------------------------------------------
    # Separate likely logical pins
    # --------------------------------------------------------

    candidates = []

    for label in labels:

        text = label["text"]

        if text in IGNORED_LABELS:
            continue

        # Very conservative candidate filtering.
        #
        # We primarily want labels that look like:
        #
        # A
        # B
        # C
        # D
        # Q
        # X
        # S
        # CLK
        # RESET_B
        #
        # but we retain longer labels too because SKY130
        # cells can have names such as RESET_B.
        #
        # We intentionally do NOT assume direction here.

        if text.startswith("sky130_"):
            continue

        candidates.append(label)

    total_candidate_pins += len(candidates)

    # --------------------------------------------------------
    # Report
    # --------------------------------------------------------

    print()
    print(f"  Text labels found : {len(labels)}")
    print(f"  Pin candidates    : {len(candidates)}")

    if layers_seen:

        print()
        print("  Label layers:")

        for layer, count in sorted(layers_seen.items()):
            print(
                f"    {layer:<12} "
                f"{count:>4}"
            )

    if labels:

        print()
        print("  LABELS:")

        for label in labels:

            print(
                f"    {label['text']:<20} "
                f"@ {label['position']}"
                f"  layer={label['layer']}/"
                f"{label['datatype']}"
            )

    else:

        print()
        print("  *** NO TEXT LABELS FOUND ***")

    if candidates:

        print()
        print("  CANDIDATE PINS:")

        for pin in candidates:

            print(
                f"    {pin['text']:<20} "
                f"@ {pin['position']}"
            )

    master_pin_data[master_name] = {
        "cell_index": cell.cell_index(),
        "bbox": bbox_dict(cell.bbox()),
        "labels": labels,
        "pins": candidates,
        "label_layers": dict(layers_seen),
    }


# ============================================================
# Build instance-level pin locations
# ============================================================

print()
print("=" * 110)
print(" INSTANCE PIN MAPPING")
print("=" * 110)

instances_output = []

instances_with_pins = 0
instances_without_pins = 0


for instance in logical_db["instances"]:

    master_name = instance["master"]

    master_data = master_pin_data.get(master_name, {})
    pins = master_data.get("pins", [])

    instance_record = {
        "id": instance["id"],
        "name": f"U{instance['id']:04d}",
        "master": master_name,
        "origin": instance["origin"],
        "transform": instance["transform"],
        "bbox": instance["bbox"],
        "pins": [],
    }

    # --------------------------------------------------------
    # Transform each master pin into top-level coordinates
    # --------------------------------------------------------

    # Locate the corresponding GDS instance transformation.
    #
    # We recreate it from the JSON transform rather than relying
    # on the original object because logical_cells.json is the
    # canonical input to this stage.

    t = instance["transform"]

    trans = pya.Trans(
        int(t["angle"]),
        bool(t["mirror"]),
        int(t["x"]),
        int(t["y"]),
    )

    for pin in pins:

        p = pin.get("position")

        if p is None:
            continue

        local_point = pya.Point(
            int(p["x"]),
            int(p["y"]),
        )

        try:
            global_point = trans * local_point
        except Exception:

            # Fallback: retain local position if the
            # transformation cannot be applied.
            global_point = local_point

        pin_record = {
            "name": pin["text"],

            "local": {
                "x": local_point.x,
                "y": local_point.y,
            },

            "global": {
                "x": global_point.x,
                "y": global_point.y,
            },

            "layer": pin["layer"],
            "datatype": pin["datatype"],
            "layer_index": pin["layer_index"],
            "layer_name": pin["layer_name"],

            "is_power": pin["is_power"],
        }

        instance_record["pins"].append(pin_record)

    if instance_record["pins"]:
        instances_with_pins += 1
    else:
        instances_without_pins += 1

    instances_output.append(instance_record)


# ============================================================
# Create output database
# ============================================================

output = {
    "metadata": {
        "source_gds": str(Path(GDSFILE).resolve()),
        "source_logical_cells": str(
            Path(INPUT_JSON).resolve()
        ),
        "top_cell": logical_db["metadata"]["top_cell"],
        "dbu": logical_db["metadata"]["dbu"],

        "logical_instance_count":
            len(logical_db["instances"]),

        "master_count":
            len(master_names),

        "total_text_labels":
            total_text_labels,

        "total_candidate_pins":
            total_candidate_pins,

        "instances_with_pins":
            instances_with_pins,

        "instances_without_pins":
            instances_without_pins,
    },

    "masters": master_pin_data,

    "instances": instances_output,
}


with open(OUTPUT_JSON, "w") as f:
    json.dump(
        output,
        f,
        indent=2,
        sort_keys=False,
    )


# ============================================================
# Final summary
# ============================================================

print()
print("=" * 110)
print(" EXTRACTION SUMMARY")
print("=" * 110)

print(
    f"Logical instances      : "
    f"{len(logical_db['instances'])}"
)

print(
    f"Cell masters            : "
    f"{len(master_names)}"
)

print(
    f"Text labels found       : "
    f"{total_text_labels}"
)

print(
    f"Candidate pins          : "
    f"{total_candidate_pins}"
)

print(
    f"Instances with pins     : "
    f"{instances_with_pins}"
)

print(
    f"Instances without pins  : "
    f"{instances_without_pins}"
)

print()
print(f"Output                  : {OUTPUT_JSON}")

print("=" * 110)
