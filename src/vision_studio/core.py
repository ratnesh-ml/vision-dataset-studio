from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

SUPPORTED = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}


@dataclass(frozen=True)
class ImageRecord:
    path: str
    width: int
    height: int
    channels: int
    brightness: float
    contrast: float
    blur_proxy: float
    sha256: str
    flags: tuple[str, ...]

    def to_dict(self):
        row = asdict(self)
        row['flags'] = list(self.flags)
        return row


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def _metrics(path: Path):
    with Image.open(path) as image:
        rgb = image.convert('RGB')
        array = np.asarray(rgb, dtype=np.float32)
    gray = array.mean(axis=2)
    gradient_x = np.diff(gray, axis=1) if gray.shape[1] > 1 else np.zeros_like(gray)
    gradient_y = np.diff(gray, axis=0) if gray.shape[0] > 1 else np.zeros_like(gray)
    blur_proxy = float(np.var(gradient_x) + np.var(gradient_y))
    return rgb.width, rgb.height, 3, float(gray.mean()), float(gray.std()), blur_proxy


def _flags(width, height, brightness, contrast, blur_proxy, duplicate=False):
    flags = []
    if min(width, height) < 64:
        flags.append('tiny_image')
    if brightness < 25:
        flags.append('too_dark')
    if brightness > 235:
        flags.append('too_bright')
    if contrast < 8:
        flags.append('low_contrast')
    if blur_proxy < 18:
        flags.append('possible_blur')
    if duplicate:
        flags.append('exact_duplicate')
    return tuple(flags)


def audit_folder(folder: str | Path, min_size=64, blur_threshold=18.0) -> dict:
    folder = Path(folder)
    paths = sorted(p for p in folder.rglob('*') if p.is_file() and p.suffix.lower() in SUPPORTED)
    raw = []
    for path in paths:
        try:
            width, height, channels, brightness, contrast, blur_proxy = _metrics(path)
            raw.append({'path': str(path), 'width': width, 'height': height, 'channels': channels, 'brightness': round(brightness, 3), 'contrast': round(contrast, 3), 'blur_proxy': round(blur_proxy, 3), 'sha256': _sha256(path)})
        except Exception as exc:
            raw.append({'path': str(path), 'error': str(exc), 'sha256': ''})
    counts = {}
    for row in raw:
        if row.get('sha256'):
            counts[row['sha256']] = counts.get(row['sha256'], 0) + 1
    records = []
    for row in raw:
        if row.get('error'):
            flags = ('unreadable',)
            row.update({'width': 0, 'height': 0, 'channels': 0, 'brightness': 0.0, 'contrast': 0.0, 'blur_proxy': 0.0})
        else:
            flags = _flags(row['width'], row['height'], row['brightness'], row['contrast'], row['blur_proxy'], counts.get(row['sha256'], 0) > 1)
            if row['width'] < min_size or row['height'] < min_size:
                flags = tuple(dict.fromkeys(flags + ('below_min_size',)))
            if row['blur_proxy'] < blur_threshold:
                flags = tuple(dict.fromkeys(flags + ('below_blur_threshold',)))
        records.append(ImageRecord(row['path'], row['width'], row['height'], row['channels'], row['brightness'], row['contrast'], row['blur_proxy'], row.get('sha256', ''), flags))
    flagged = [r for r in records if r.flags]
    return {'folder': str(folder), 'images': len(records), 'flagged': len(flagged), 'clean': len(records) - len(flagged), 'records': [r.to_dict() for r in records]}


def make_sample_images(folder: str | Path, count=12):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    for i in range(count):
        image = Image.new('RGB', (160, 120), (35 + i * 8, 55 + i * 4, 78 + i * 3))
        draw = ImageDraw.Draw(image)
        draw.rectangle((25, 25, 135, 95), outline=(220, 230, 245), width=3)
        draw.ellipse((55 + i % 5, 45, 90 + i % 5, 80), fill=(235, 180, 90))
        if i % 4 == 0:
            draw.line((20, 60, 140, 60), fill=(240, 80, 80), width=2)
        image.save(folder / f'sample_{i:02d}.png')
    if count >= 2:
        (folder / 'duplicate.png').write_bytes((folder / 'sample_00.png').read_bytes())


def write_json(result: dict, path: str | Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding='utf-8')


def write_html(result: dict, path: str | Path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for row in result['records']:
        status = 'review' if row['flags'] else 'clean'
        rows.append('<tr><td>{path}</td><td>{width}×{height}</td><td>{brightness:.1f}</td><td>{contrast:.1f}</td><td>{blur_proxy:.1f}</td><td class="{status}">{flags}</td></tr>'.format(path=row['path'], width=row['width'], height=row['height'], brightness=row['brightness'], contrast=row['contrast'], blur_proxy=row['blur_proxy'], status=status, flags=', '.join(row['flags']) or 'clean'))
    html = '<!doctype html><meta charset="utf-8"><title>Vision Dataset Studio report</title><style>body{{font:15px system-ui;margin:40px;color:#172033}}table{{border-collapse:collapse;width:100%}}th,td{{padding:10px;border-bottom:1px solid #d9e0ea;text-align:left}}th{{background:#172033;color:white}}.review{{color:#a33}}.clean{{color:#176b47}}</style><h1>Vision Dataset Studio</h1><p>{images} images · <b>{flagged} flagged</b> · {clean} clean</p><table><tr><th>Path</th><th>Size</th><th>Brightness</th><th>Contrast</th><th>Blur proxy</th><th>Decision</th></tr>{rows}</table>'.format(images=result['images'], flagged=result['flagged'], clean=result['clean'], rows=''.join(rows))
    path.write_text(html, encoding='utf-8')
