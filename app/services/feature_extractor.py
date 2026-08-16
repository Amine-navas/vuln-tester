"""Extraction de features pour texte ou fichiers uploadés."""

import hashlib
import math
from typing import Any

SUSPICIOUS_EXTENSIONS = {
    '.exe', '.dll', '.bat', '.cmd', '.com', '.scr', '.js', '.jse', '.vbs', '.vbe',
    '.ps1', '.psm1', '.hta', '.jar', '.msi', '.reg', '.lnk', '.apk', '.py', '.sh', '.bash'
}

SUSPICIOUS_KEYWORDS = (
    'powershell', 'cmd.exe', 'rundll32', 'wget ', 'curl ', 'base64', 'eval(',
    'from ctypes', 'wscript.shell', 'createprocess', 'http://', 'https://',
    'winhttp', 'microsoft.net', 'runas', 'powershell.exe'
)


def compute_sha256(sample: Any) -> str:
    """Calcule le hash SHA256 d'un objet bytes/str."""
    raw = _coerce_bytes(sample)
    return hashlib.sha256(raw).hexdigest()


def is_pe_file(data: Any) -> bool:
    """Détecte les exécutables Windows PE à partir d'un Magic Number MZ/PE."""
    raw = _coerce_bytes(data)
    if len(raw) < 64:
        return False
    return raw.startswith(b'MZ') and b'PE\x00\x00' in raw[:256]


def _coerce_bytes(sample: Any) -> bytes:
    if sample is None:
        return b''
    if isinstance(sample, bytes):
        return sample
    if isinstance(sample, bytearray):
        return bytes(sample)
    return str(sample).encode('utf-8', errors='ignore')


def _shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    counts = {}
    for byte in data:
        counts[byte] = counts.get(byte, 0) + 1
    length = len(data)
    entropy = 0.0
    for count in counts.values():
        probability = count / length
        entropy -= probability * math.log2(probability)
    return round(entropy, 3)


def extract_features(sample: Any, file_name: str = '') -> dict:
    """Extraire des caractéristiques utiles pour évaluer un fichier ou un texte.

    Ajout:
    - comptage d'occurences de mots-clés de CV/resume (resume_hits)
    - détection 'is_likely_resume' pour réduire les faux positifs sur les CVs
    """
    raw = _coerce_bytes(sample)
    text = raw.decode('utf-8', errors='ignore')

    extension = ''
    if file_name:
        extension = file_name.lower()[file_name.rfind('.'):] if '.' in file_name else ''

    suspicious_extension = extension in SUSPICIOUS_EXTENSIONS
    suspicious_hits = 0
    lowered = text.lower()
    for keyword in SUSPICIOUS_KEYWORDS:
        suspicious_hits += lowered.count(keyword.lower())

    # Resume / CV heuristics (common words present in CVs)
    RESUME_KEYWORDS = (
        'curriculum vitae', 'cv', 'résumé', 'resume', 'experience', 'expérience',
        'education', 'formation', 'skills', 'compétences', 'certificat', 'certifications',
        'linkedin', 'portfolio', 'email', 'tél', 'telephone', 'phone', 'address'
    )
    resume_hits = 0
    for rk in RESUME_KEYWORDS:
        resume_hits += lowered.count(rk)

    length = len(text)
    num_digits = sum(1 for c in text if c.isdigit())
    num_lines = text.count('\n') + 1 if text else 0
    printable = sum(1 for ch in text if ch.isprintable() or ch in '\r\n\t')
    printable_ratio = (printable / length) if length else 0.0
    entropy = _shannon_entropy(raw)
    is_binary_like = bool(raw) and entropy > 4.2 and printable_ratio < 0.85
    is_pe = is_pe_file(raw) or extension in {'.exe', '.dll', '.sys'}
    sha256 = compute_sha256(raw)

    # Heuristic: consider it likely a resume when it contains multiple resume keywords
    is_likely_resume = (resume_hits >= 2) and printable_ratio > 0.9 and not is_pe and not suspicious_extension

    return {
        'length': length,
        'num_digits': num_digits,
        'num_lines': num_lines,
        'file_size': len(raw),
        'entropy': entropy,
        'printable_ratio': round(printable_ratio, 3),
        'suspicious_hits': suspicious_hits,
        'suspicious_extension': suspicious_extension,
        'is_binary_like': is_binary_like,
        'is_pe': is_pe,
        'sha256': sha256,
        'file_name': file_name,
        'extension': extension,
        'resume_hits': resume_hits,
        'is_likely_resume': bool(is_likely_resume),
    }
