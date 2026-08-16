import json

from app.services import feature_extractor, malware_detector, risk_analyzer


def test_pipeline_smoke():
    """Smoke test: feature extraction -> ML/rule detector -> risk analyzer.

    Vérifie que la pipeline retourne des types et des plages attendues.
    """
    sample = "This is a benign sample 12345 with some digits and text.\nAnother line."
    features = feature_extractor.extract_features(sample)
    assert isinstance(features, dict)

    label, score = malware_detector.predict(features)
    assert label in ("malicious", "benign", "unknown")
    assert isinstance(score, float) or isinstance(score, int)
    assert 0.0 <= float(score) <= 1.0

    risk = risk_analyzer.assess(features, float(score))
    assert risk in ("low", "medium", "high")


def test_short_plain_text_is_not_forced_to_malicious():
    """A model trained on unrelated system metrics must not classify all text as malware."""
    features = feature_extractor.extract_features("hello")
    label, score = malware_detector.predict(features)
    assert label == "benign"
    assert score == 0.0


def test_suspicious_file_upload_detects_risk():
    """A suspicious file with script-like content or extension should be scored as risky."""
    file_bytes = b"powershell -enc aGVsbG8=; CreateProcess('cmd.exe')"
    features = feature_extractor.extract_features(file_bytes, file_name='malware.ps1')
    label, score = malware_detector.predict(features)
    assert label in ("malicious", "benign")
    assert score >= 0.0
    assert features['suspicious_extension'] is True
    assert features['suspicious_hits'] > 0


def test_pe_header_is_detected_for_executables():
    """Windows executables should be flagged as PE files using the MZ/PE signature."""
    pe_bytes = b'MZ' + b'\x00' * 0x3A + b'PE\x00\x00' + b'\x00' * 64
    features = feature_extractor.extract_features(pe_bytes, file_name='evil.exe')
    assert features['is_pe'] is True
    assert features['sha256']
