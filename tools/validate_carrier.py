"""Recheck the released carrier with KiCad 10 and the inherited R2 invariants."""

import argparse
import collections
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOARD = "din_isolated_SPI.kicad_pcb"
SCHEMATIC = "din_isolated_SPI.kicad_sch"
PROJECT = "din_isolated_SPI.kicad_pro"


def parse(text):
    stack, root = [], []
    for token in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text):
        if token == "(":
            node = []
            (stack[-1] if stack else root).append(node)
            stack.append(node)
        elif token == ")":
            stack.pop()
        else:
            stack[-1].append(token)
    if stack or len(root) != 1:
        raise ValueError("Invalid S-expression")
    return root[0]


def encode(node):
    return "(" + " ".join(encode(x) if isinstance(x, list) else x for x in node) + ")"


def children(node, name):
    return [x for x in node if isinstance(x, list) and x[0] == name]


def child(node, name):
    return next(iter(children(node, name)), None)


def reference(fp):
    return json.loads(next(x[2] for x in children(fp, "property") if x[1] == '"Reference"'))


def pad_memberships(board):
    numeric = {x[1]: x[2] for x in children(board, "net") if len(x) == 3}
    result = collections.defaultdict(list)
    for fp in children(board, "footprint"):
        for pad in children(fp, "pad"):
            net = child(pad, "net")
            if net:
                result[numeric.get(net[1], net[-1])].append(reference(fp) + "." + json.loads(pad[1]))
    return {name: sorted(pins) for name, pins in result.items()}


def validate_invariants():
    original = json.loads((ROOT / "validation" / "source_invariants.json").read_text(encoding="utf-8"))
    board = parse((ROOT / BOARD).read_text(encoding="utf-8"))
    fps = {}
    for fp in children(board, "footprint"):
        pad_data = []
        for pad in children(fp, "pad"):
            geometry = [x for x in pad if not (isinstance(x, list) and x[0] in ("net", "uuid", "tstamp"))]
            pad_data.append(encode(geometry))
        fps[reference(fp)] = {"at": child(fp, "at"), "layer": child(fp, "layer"), "pads": sorted(pad_data)}
    assert fps == original["footprints"], "Component placement or pad geometry changed"

    memberships = pad_memberships(board)
    assert sorted(memberships.values()) == original["net_memberships"], "Pad net memberships changed"
    numeric = {x[1]: x[2] for x in children(board, "net") if len(x) == 3}
    routes = []
    for item in board:
        if not isinstance(item, list) or item[0] not in ("segment", "via", "arc"):
            continue
        net = child(item, "net")
        name = numeric.get(net[1], net[-1])
        geometry = [x for x in item if not (isinstance(x, list) and x[0] in ("net", "uuid", "tstamp"))]
        routes.append(encode(geometry) + " " + json.dumps(memberships.get(name, []), separators=(",", ":")))
    expected_routes = collections.Counter(original["route_geometry"])
    expected_routes.subtract(original["removed_routes"])
    assert collections.Counter(routes) == +expected_routes, "Copper routing or its net changed"

    edges = []
    for item in board:
        if not isinstance(item, list) or item[0] not in ("gr_line", "gr_arc"):
            continue
        if child(item, "layer")[1] == '"Edge.Cuts"':
            edges.append(encode([item[0]] + [x for x in item if isinstance(x, list) and x[0] in ("start", "mid", "end")]))
    assert sorted(edges) == original["edges"], "Outline or isolation slot changed"
    assert len(original["slot_edges"]) == 4 and len([e for e in edges if e.startswith("(gr_arc ")]) == 4
    print("R2 component/pad, net, route, four-corner and slot invariants: PASS")
    return board


def validate_rules():
    project = json.loads((ROOT / PROJECT).read_text(encoding="utf-8"))
    settings = project["net_settings"]
    classes = {x["name"]: x for x in settings["classes"]}
    assert classes["Default"]["clearance"] == 0.15 and classes["Default"]["track_width"] == 0.25
    assert classes["Power"]["clearance"] == 0.5 and classes["Power"]["track_width"] == 0.5
    assigned = {x["pattern"] for x in settings["netclass_patterns"] if x["netclass"] == "Power"}
    assert assigned == {"GND_C", "GND_I", "3V3_C", "3V3_I"}
    assert not project["board"]["design_settings"].get("drc_exclusions", [])
    print("Source 0.15 mm Default / 0.5 mm Power constraints and exclusions: PASS")


def validate_models(board, cli):
    standard = cli.parent.parent / "share" / "kicad" / "3dmodels"
    checked = set()
    for fp in children(board, "footprint"):
        for model in children(fp, "model"):
            name = json.loads(model[1])
            if name.startswith("${KIPRJMOD}/"):
                path = ROOT / name.removeprefix("${KIPRJMOD}/")
            elif name.startswith("${KICAD10_3DMODEL_DIR}/"):
                path = standard / name.removeprefix("${KICAD10_3DMODEL_DIR}/")
            else:
                raise AssertionError(f"Unresolved model variable: {name}")
            assert path.is_file() and path.stat().st_size, f"Missing or empty model: {path}"
            checked.add(name)
    print(f"Referenced model paths: {len(checked)} exist (model accuracy not assessed)")


def normalize(path):
    data = path.read_bytes().replace(b"\r\n", b"\n")
    path.write_bytes(data)


def run(cli, *args):
    subprocess.run([str(cli), *args], cwd=ROOT, check=True)


def report(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", type=Path, default=Path(r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"))
    args = parser.parse_args()
    cli = args.cli.resolve()
    assert cli.is_file(), f"KiCad CLI not found: {cli}"
    for folder in ("carrier_legacy.pretty", "wemos_d1_mini.pretty", "Whatnick_logo.pretty"):
        for path in (ROOT / folder).glob("*.kicad_mod"):
            normalize(path)
    for path in ("fp-lib-table", "sym-lib-table", "carrier_power.kicad_sym", "carrier_symbols.kicad_sym",
                 r"validation\source_invariants.json"):
        normalize(ROOT / path)
    validate_rules()
    run(cli, "sch", "erc", "--format", "json", "--severity-all", "--exit-code-violations",
        "-o", r"validation\erc.json", SCHEMATIC)
    run(cli, "pcb", "drc", "--refill-zones", "--save-board", "--schematic-parity", "--format", "json",
        "--severity-all", "--exit-code-violations", "-o", r"validation\drc.json", BOARD)
    for path in (BOARD, SCHEMATIC, PROJECT, r"validation\erc.json", r"validation\drc.json"):
        normalize(ROOT / path)

    erc, drc = report(r"validation\erc.json"), report(r"validation\drc.json")
    assert not any(sheet["violations"] for sheet in erc["sheets"])
    assert not drc["violations"] and not drc["unconnected_items"] and not drc["schematic_parity"]
    assert set(erc["included_severities"]) == {"error", "warning", "exclusion"}
    assert set(drc["included_severities"]) == {"error", "warning", "exclusion"}
    assert {x["key"] for x in erc["ignored_checks"]} == {
        "single_global_label", "four_way_junction", "simulation_model_issue", "footprint_filter"}
    assert {x["key"] for x in drc["ignored_checks"]} == {
        "missing_courtyard", "track_not_centered_on_via", "tuning_profile_track_geometries",
        "footprint_filters_mismatch", "footprint_type_mismatch"}
    board = validate_invariants()
    validate_models(board, cli)
    files = [BOARD, SCHEMATIC, PROJECT, "fp-lib-table", "sym-lib-table", "carrier_power.kicad_sym",
             "carrier_symbols.kicad_sym", "validation/source_invariants.json", "validation/erc.json",
             "validation/drc.json", "mechanical/din_isolated_SPI-v2-board.step"]
    files.extend(str(p.relative_to(ROOT)).replace("\\", "/") for folder in
                 ("carrier_legacy.pretty", "wemos_d1_mini.pretty", "Whatnick_logo.pretty")
                 for p in sorted((ROOT / folder).glob("*.kicad_mod")))
    hashes = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in files}
    (ROOT / "validation" / "manifest.json").write_text(json.dumps({
        "kicad_version": drc["kicad_version"], "sha256": hashes,
        "erc": 0, "drc": 0, "unconnected": 0, "schematic_parity": 0,
    }, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("ERC / DRC / unconnected / schematic parity: 0 / 0 / 0 / 0")


if __name__ == "__main__":
    main()
