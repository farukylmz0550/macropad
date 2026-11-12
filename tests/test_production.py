import csv
import hashlib
import json
import re
import struct
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GERBER_ZIP = ROOT / "production/gerber/macropad.zip"


class ProductionPackageTest(unittest.TestCase):
    def test_easyeda_sources_are_valid_json(self):
        for relative in ("hardware/schematic.json", "hardware/pcb_easyeda.pcbdoc"):
            with self.subTest(path=relative):
                data = json.loads((ROOT / relative).read_text(encoding="utf-8"))
                self.assertIsInstance(data, dict)
                self.assertTrue(data)

    def test_cloud_schematic_signal_map(self):
        schematic = (ROOT / "hardware/schematic.json").read_text(encoding="utf-8")
        for label in (
            "OLED: D2, D3",
            "KY-040: D4, D5, D6",
            "SW1 / SW2 / SW3: D7 / D8 / D9",
            "SW4 / S5 / SW6: D12 / D11 / D10",
        ):
            self.assertIn(label, schematic)

    def test_required_gerber_and_drill_files(self):
        required = {
            "Gerber_TopLayer.GTL",
            "Gerber_BottomLayer.GBL",
            "Gerber_TopSilkscreenLayer.GTO",
            "Gerber_TopSolderMaskLayer.GTS",
            "Gerber_BottomSolderMaskLayer.GBS",
            "Gerber_BoardOutlineLayer.GKO",
            "Drill_PTH_Through.DRL",
            "Drill_PTH_Through_Via.DRL",
            "Drill_NPTH_Through.DRL",
        }
        with zipfile.ZipFile(GERBER_ZIP) as archive:
            names = set(archive.namelist())
            self.assertIsNone(archive.testzip())
        self.assertTrue(required <= names, sorted(required - names))
        self.assertFalse(any("paste" in name.lower() or "cpl" in name.lower() for name in names))

    def test_outline_dimensions(self):
        with zipfile.ZipFile(GERBER_ZIP) as archive:
            outline = archive.read("Gerber_BoardOutlineLayer.GKO").decode("ascii")
        coordinates = [
            (int(x) / 100000, int(y) / 100000)
            for x, y in re.findall(r"X(\d+)Y(\d+)D0[12]\*", outline)
        ]
        self.assertGreaterEqual(len(coordinates), 4)
        width = max(x for x, _ in coordinates) - min(x for x, _ in coordinates)
        height = max(y for _, y in coordinates) - min(y for _, y in coordinates)
        self.assertAlmostEqual(width, 68.58, places=2)
        self.assertAlmostEqual(height, 53.34, places=2)

    def test_bom_includes_connectors_and_mates(self):
        with (ROOT / "production/bom.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        designators = " ".join(row["Designators"] for row in rows)
        for designator in ("SW1", "S5", "SW6", "SSD1306", "KY-040", "U1"):
            self.assertIn(designator, designators)
        mating_parts = " ".join(row["Required mating part"] for row in rows)
        for housing in ("XHP-2", "XHP-4", "XHP-5"):
            self.assertIn(housing, mating_parts)

    def test_preview_pngs(self):
        for name in ("pcb_front.png", "pcb_back.png"):
            raw = (ROOT / "docs/images" / name).read_bytes()
            self.assertEqual(raw[:8], b"\x89PNG\r\n\x1a\n")
            width, height = struct.unpack(">II", raw[16:24])
            self.assertGreaterEqual(width, 600)
            self.assertGreaterEqual(height, 400)

    def test_checksum_manifest(self):
        manifest = ROOT / "production/checksums.sha256"
        self.assertTrue(manifest.is_file())
        for line in manifest.read_text(encoding="ascii").splitlines():
            expected, relative = line.split("  ", 1)
            payload = (ROOT / relative).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), expected, relative)


if __name__ == "__main__":
    unittest.main()
