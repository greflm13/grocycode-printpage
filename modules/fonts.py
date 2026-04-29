import os
import sys
import json
import hashlib
import subprocess

from dataclasses import dataclass

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont, TTFError
from PySide6.QtWidgets import QComboBox
from PySide6.QtGui import QFontDatabase

if sys.platform.startswith("win"):
    import winreg


@dataclass(frozen=True)
class FontEntry:
    family: str
    weight: int
    italic: bool
    path: str
    font_id: str | None  # ReportLab font name (hash)
    reportlab_ok: bool


def register_with_reportlab(path: str) -> tuple[str | None, bool]:
    """
    Try to register a font file with ReportLab.
    Returns (font_id, success).
    """
    font_id = hashlib.md5(path.encode("utf-8")).hexdigest()[:8]

    try:
        if font_id not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(font_id, path))
        return font_id, True
    except TTFError:
        return None, False
    except Exception:
        return None, False


def enumerate_linux_fonts() -> list[FontEntry]:
    db = QFontDatabase()
    result: list[FontEntry] = []

    proc = subprocess.run(
        ["fc-list", "--format=%{file}|%{family}|%{style}\n"],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )

    seen = set()

    for line in proc.stdout.splitlines():
        path, family, style = line.split("|", 2)
        family = family.split(",")[0]
        key = (path, family, style)
        if key in seen:
            continue
        seen.add(key)

        qfont = db.font(family, style, 12)

        font_id, ok = register_with_reportlab(path)

        result.append(
            FontEntry(
                family=family,
                weight=qfont.weight(),
                italic=qfont.italic(),
                path=path,
                font_id=font_id,
                reportlab_ok=ok,
            )
        )

    return result


def enumerate_windows_fonts() -> list[FontEntry]:
    db = QFontDatabase()
    result: list[FontEntry] = []

    font_dirs = [
        os.path.join(os.environ["WINDIR"], "Fonts"),
        os.path.join(
            os.environ.get("LOCALAPPDATA", ""),
            "Microsoft",
            "Windows",
            "Fonts",
        ),
    ]

    registry_sources = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts", font_dirs[0]),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts", font_dirs[1]),
    ]

    paths: set[str] = set()

    for root, reg_path, base_dir in registry_sources:
        try:
            with winreg.OpenKey(root, reg_path) as key:
                for i in range(winreg.QueryInfoKey(key)[1]):
                    _, value, _ = winreg.EnumValue(key, i)
                    if os.path.isabs(value):
                        paths.add(value)
                    else:
                        p = os.path.join(base_dir, value)
                        if os.path.exists(p):
                            paths.add(p)
        except FileNotFoundError:
            pass

    for d in font_dirs:
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            if fn.lower().endswith((".ttf", ".otf", ".ttc")):
                paths.add(os.path.join(d, fn))

    for family in db.families():
        for style in db.styles(family):
            qfont = db.font(family, style, 12)

            for path in paths:
                if family.lower().replace(" ", "") in os.path.basename(path).lower():
                    font_id, ok = register_with_reportlab(path)
                    result.append(
                        FontEntry(
                            family=family,
                            weight=qfont.weight(),
                            italic=qfont.italic(),
                            path=path,
                            font_id=font_id,
                            reportlab_ok=ok,
                        )
                    )
                    break

    return result


def enumerate_macos_fonts() -> list[FontEntry]:
    db = QFontDatabase()
    result: list[FontEntry] = []

    proc = subprocess.run(
        ["system_profiler", "SPFontsDataType", "-json"],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )

    data = json.loads(proc.stdout)
    font_items = data.get("SPFontsDataType", [])

    paths_by_family: dict[str, list[str]] = {}

    for item in font_items:
        family = item.get("_name")
        path = item.get("path")
        if family and path:
            paths_by_family.setdefault(family.lower(), []).append(path)

    for family in db.families():
        for style in db.styles(family):
            qfont = db.font(family, style, 12)
            paths = paths_by_family.get(family.lower())
            if not paths:
                continue

            path = paths[0]
            font_id, ok = register_with_reportlab(path)

            result.append(
                FontEntry(
                    family=family,
                    weight=qfont.weight(),
                    italic=qfont.italic(),
                    path=path,
                    font_id=font_id,
                    reportlab_ok=ok,
                )
            )

    return result


def enumerate_system_fonts() -> list[FontEntry]:
    if sys.platform.startswith("win"):
        return enumerate_windows_fonts()
    if sys.platform.startswith("linux"):
        return enumerate_linux_fonts()
    if sys.platform == "darwin":
        return enumerate_macos_fonts()
    raise RuntimeError("Unsupported platform")


def find_font_from_inventory(fonts: list[FontEntry], family: str, weight: int, italic: bool) -> FontEntry:
    candidates = [f for f in fonts if f.family == family and f.italic == italic]

    if not candidates:
        raise RuntimeError(f"No font found for {family}")

    return min(candidates, key=lambda f: abs(f.weight - weight))


class PdfSafeFontComboBox(QComboBox):
    def __init__(self, fonts: list[FontEntry], parent=None):
        super().__init__(parent)

        self._fonts = fonts
        self._families = sorted({f.family for f in fonts if f.reportlab_ok})

        for fam in self._families:
            self.addItem(fam)

    def current_font_entry(self) -> FontEntry:
        family = self.currentText()
        qfont = self.font()

        return find_font_from_inventory(
            self._fonts,
            family,
            qfont.weight(),
            qfont.italic(),
        )
