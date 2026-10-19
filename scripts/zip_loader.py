#!/usr/bin/env python3
"""
zip_loader.py — load a pipeline results archive (zip with manifest.json at its root)
and resolve its files through the manifest.

The archive is produced by build_agentic_archive.py in the jordan-hsa-optimization
pipeline. Paths in manifest.json are relative to the archive root. This loader never
builds file names from the network/disease labels: it only follows manifest paths.

Python use (from the repository root, which is the agent's working directory):

    from scripts.zip_loader import load_archive
    b = load_archive("skills/jordan-climate-health-models/data/archives")  # file or dir
    b.path("hsa_boundaries")                 # -> Path to the GeoJSON
    b.dir("sensitivity")                     # -> Path to the folder
    b.glob("model_results", "*_model_summary.json")   # -> [Path, ...]
    b.manifest["meta"]["synthetic"]          # -> True

Command line (a quick check that an archive loads correctly):

    python scripts/zip_loader.py skills/jordan-climate-health-models/data/archives

Extraction goes to <zip folder>/_loaded/<zip name>/ (falls back to the system temp
folder if that is not writable) and is reused while the zip is unchanged.
Standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

MANIFEST_NAME = "manifest.json"
MARKER_NAME = ".archive_sha256"
SECTIONS = ("model", "HEFTE")                       # sections the spec defines
# Section keys that describe the run; every other string value is a path.
METADATA_KEYS = {"network", "hsa_mode", "boundary_version", "disease_focus_input",
                 "disease_group", "disease_slug"}
REQUIRED_METADATA = ("network", "hsa_mode", "boundary_version", "disease_slug")
MAX_MEMBERS = 5000
MAX_TOTAL_BYTES = 1024 ** 3                         # 1 GiB uncompressed


class ArchiveError(Exception):
    """The archive is missing, malformed, unsafe, or inconsistent with its manifest."""


# --------------------------------------------------------------------------- bundle
@dataclass
class Bundle:
    root: Path          # folder the archive was extracted to (archive root)
    manifest: dict
    zip_path: Path

    # -- manifest access
    def sections(self) -> list[str]:
        return [s for s in SECTIONS if isinstance(self.manifest.get(s), dict)]

    def path_keys(self, section: str) -> list[str]:
        sec = self.manifest[section]
        return [k for k, v in sec.items() if k not in METADATA_KEYS and isinstance(v, str)]

    def _lookup(self, key: str, section: str | None) -> tuple[str, str]:
        order = [section] if section else self.sections()
        for s in order:
            sec = self.manifest.get(s)
            if isinstance(sec, dict) and isinstance(sec.get(key), str) and key not in METADATA_KEYS:
                return s, sec[key]
        where = f"section {section!r}" if section else f"sections {self.sections()}"
        raise ArchiveError(f"manifest has no path entry {key!r} in {where}")

    def _resolve(self, rel: str) -> Path:
        pp = PurePosixPath(rel)
        if pp.is_absolute() or ".." in pp.parts:
            raise ArchiveError(f"unsafe path in manifest: {rel!r}")
        p = (self.root / Path(*pp.parts)).resolve()
        if self.root.resolve() not in p.parents and p != self.root.resolve():
            raise ArchiveError(f"manifest path escapes the archive: {rel!r}")
        return p

    # -- public lookups
    def path(self, key: str, section: str | None = None) -> Path:
        """Path of a file entry (e.g. 'hsa_boundaries'). Raises if it is not a file."""
        _, rel = self._lookup(key, section)
        p = self._resolve(rel)
        if not p.is_file():
            raise ArchiveError(f"{key!r} -> {rel!r} is not a file in the archive")
        return p

    def dir(self, key: str, section: str | None = None) -> Path:
        """Path of a folder entry (e.g. 'sensitivity'). Raises if it is not a folder."""
        _, rel = self._lookup(key, section)
        p = self._resolve(rel)
        if not p.is_dir():
            raise ArchiveError(f"{key!r} -> {rel!r} is not a folder in the archive")
        return p

    def glob(self, key: str, pattern: str = "*", section: str | None = None,
             recursive: bool = True) -> list[Path]:
        """Files under a folder entry matching a pattern, sorted."""
        d = self.dir(key, section)
        it = d.rglob(pattern) if recursive else d.glob(pattern)
        return sorted(p for p in it if p.is_file())

    def describe(self) -> str:
        meta = self.manifest.get("meta", {})
        lines = [f"bundle     : {meta.get('bundle_key', '(no bundle_key)')}",
                 f"synthetic  : {meta.get('synthetic', '(not stated)')}",
                 f"n_hsas     : {meta.get('n_hsas', '(not stated)')}",
                 f"sections   : {', '.join(self.sections())}",
                 f"extracted  : {self.root}"]
        for s in self.sections():
            lines.append(f"[{s}]")
            for k in self.path_keys(s):
                rel = self.manifest[s][k]
                p = self._resolve(rel)
                if p.is_dir():
                    n = sum(1 for f in p.rglob("*") if f.is_file())
                    lines.append(f"  {k:16s} {rel}  (folder, {n} files)")
                else:
                    lines.append(f"  {k:16s} {rel}  ({p.stat().st_size / 1024:.0f} KB)")
        return "\n".join(lines)


# ------------------------------------------------------------------- finding the zip
def _find_zip(source: Path, key: str | None) -> Path:
    if source.is_file():
        return source
    if not source.is_dir():
        raise ArchiveError(f"archive not found: {source}")
    zips = sorted(p for p in source.glob("*.zip") if p.is_file())
    if key:
        zips = [p for p in zips if key in p.name]
    if len(zips) == 1:
        return zips[0]
    if not zips:
        raise ArchiveError(f"no .zip archive{' matching ' + repr(key) if key else ''} in {source}")
    raise ArchiveError(f"{len(zips)} archives in {source}; pass key=... to choose one: "
                       + ", ".join(p.name for p in zips))


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------- validation
def _read_and_validate(zf: zipfile.ZipFile) -> dict:
    infos = zf.infolist()
    names = [i.filename for i in infos]
    if MANIFEST_NAME not in names:
        raise ArchiveError(f"{MANIFEST_NAME} is not at the archive root "
                           f"(first entries: {names[:3]})")
    if len(infos) > MAX_MEMBERS:
        raise ArchiveError(f"archive has {len(infos)} entries (limit {MAX_MEMBERS})")
    if sum(i.file_size for i in infos) > MAX_TOTAL_BYTES:
        raise ArchiveError("archive is too large when uncompressed")
    for n in names:
        pp = PurePosixPath(n)
        if pp.is_absolute() or ".." in pp.parts or "\\" in n:
            raise ArchiveError(f"unsafe entry name in archive: {n!r}")
    try:
        manifest = json.loads(zf.read(MANIFEST_NAME))
    except Exception as e:
        raise ArchiveError(f"{MANIFEST_NAME} is not valid JSON: {e}") from e
    if not isinstance(manifest, dict):
        raise ArchiveError(f"{MANIFEST_NAME} must be a JSON object")
    present = [s for s in SECTIONS if s in manifest]
    if not present:
        raise ArchiveError(f"{MANIFEST_NAME} has none of the expected sections {SECTIONS}")
    for s in present:
        if not isinstance(manifest[s], dict):
            raise ArchiveError(f"manifest section {s!r} must be an object")
        missing = [k for k in REQUIRED_METADATA if k not in manifest[s]]
        if missing:
            raise ArchiveError(f"manifest section {s!r} is missing keys: {missing}")
    return manifest


def _extract(zf: zipfile.ZipFile, dest: Path) -> None:
    """Extract into dest, counting real bytes written (not trusting zip headers)."""
    dest_resolved = dest.resolve()
    total = 0
    for info in zf.infolist():
        if info.is_dir():
            continue
        target = (dest / info.filename).resolve()
        if dest_resolved not in target.parents:
            raise ArchiveError(f"entry would be written outside the target: {info.filename!r}")
        target.parent.mkdir(parents=True, exist_ok=True)
        with zf.open(info) as src, open(target, "wb") as out:
            while True:
                chunk = src.read(1 << 20)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_TOTAL_BYTES:
                    raise ArchiveError("archive expands beyond the size limit")
                out.write(chunk)


def _check_against_manifest(bundle: Bundle) -> None:
    problems = []
    for s in bundle.sections():
        for k in bundle.path_keys(s):
            rel = bundle.manifest[s][k]
            try:
                p = bundle._resolve(rel)
            except ArchiveError as e:
                problems.append(str(e))
                continue
            if not p.exists():
                problems.append(f"{s}.{k} -> {rel!r} does not exist in the archive")
            elif rel.endswith("/") and not p.is_dir():
                problems.append(f"{s}.{k} -> {rel!r} should be a folder")
            elif rel.endswith("/") and not any(f.is_file() for f in p.rglob("*")):
                problems.append(f"{s}.{k} -> {rel!r} is an empty folder")
    for rel in bundle.manifest.get("meta", {}).get("files", []) or []:
        try:
            if not bundle._resolve(rel).is_file():
                problems.append(f"meta.files lists {rel!r} but it is not in the archive")
        except ArchiveError as e:
            problems.append(str(e))
    if problems:
        raise ArchiveError("archive does not match its manifest:\n  " + "\n  ".join(problems[:15]))


# ------------------------------------------------------------------------- public
def load_archive(source, dest=None, key: str | None = None) -> Bundle:
    """Validate and extract an archive, and return a Bundle.

    source : a .zip file, or a folder holding exactly one .zip (use key= to pick one)
    dest   : extraction folder (default: <zip folder>/_loaded/<zip stem>/)
    Extraction is skipped when dest already holds this exact zip (same SHA-256).
    """
    zip_path = _find_zip(Path(source), key)
    try:
        zf = zipfile.ZipFile(zip_path)
    except zipfile.BadZipFile as e:
        raise ArchiveError(f"{zip_path.name} is not a valid zip file") from e
    with zf:
        manifest = _read_and_validate(zf)
        digest = _sha256(zip_path)
        candidates = [Path(dest)] if dest else [
            zip_path.parent / "_loaded" / zip_path.stem,
            Path(tempfile.gettempdir()) / "wenokn_archives" / zip_path.stem,
        ]
        last_err = None
        for target in candidates:
            marker = target / MARKER_NAME
            try:
                if marker.is_file() and marker.read_text().strip() == digest:
                    break                                    # already extracted, unchanged
                tmp = target.with_name(target.name + f".tmp{id(zf)}")
                if tmp.exists():
                    shutil.rmtree(tmp)
                tmp.mkdir(parents=True)
                try:
                    _extract(zf, tmp)
                    (tmp / MARKER_NAME).write_text(digest)
                    if target.exists():
                        shutil.rmtree(target)
                    tmp.rename(target)
                finally:
                    if tmp.exists():
                        shutil.rmtree(tmp, ignore_errors=True)
                break
            except OSError as e:                             # not writable -> try next place
                last_err = e
        else:
            raise ArchiveError(f"could not extract the archive anywhere: {last_err}")
    bundle = Bundle(root=target, manifest=manifest, zip_path=zip_path)
    _check_against_manifest(bundle)
    return bundle


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Load a results archive and show what the manifest resolves to.")
    ap.add_argument("source", help="a .zip file, or a folder containing one")
    ap.add_argument("--dest", default=None, help="extraction folder")
    ap.add_argument("--key", default=None, help="pick the archive whose name contains this")
    args = ap.parse_args(argv)
    try:
        bundle = load_archive(args.source, dest=args.dest, key=args.key)
    except ArchiveError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(bundle.describe())
    print("OK: archive loaded and every manifest path resolves.")
    return 0


if __name__ == "__main__":
    sys.exit(main())