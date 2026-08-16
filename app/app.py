from flask import Flask, jsonify, request, send_from_directory, abort
from pathlib import Path
import os
import sys
import subprocess
import json
import time
from app.services import feature_extractor, malware_detector, risk_analyzer

PROJECT_ROOT = Path(__file__).resolve().parent.parent
app = Flask(__name__, static_folder=str(PROJECT_ROOT / 'static'), static_url_path='/static')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/scan', methods=['POST'])
def scan():
    uploaded_file = None
    if request.files:
        uploaded_file = request.files.get('file') or next(iter(request.files.values()), None)

    if uploaded_file is not None and getattr(uploaded_file, 'filename', ''):
        file_bytes = uploaded_file.read()
        file_name = uploaded_file.filename or 'uploaded_file'
        features = feature_extractor.extract_features(file_bytes, file_name=file_name)
        hash_value = features.get('sha256')
        known_label, known_score = ('unknown', 0.0)
        if hash_value:
            known_label, known_score = malware_detector.predict_from_hash(hash_value)
        if known_label != 'unknown':
            label, score = known_label, known_score
        else:
            label, score = malware_detector.predict(features)
        risk = risk_analyzer.assess(features, score)
        result = {
            'result': label,
            'score': score,
            'risk': risk,
            'features': features,
            'file_name': file_name,
            'sha256': hash_value,
            'source': 'file',
            'hash_known': known_label != 'unknown',
            'hash_status': 'known_malicious' if known_label == 'malicious' else 'known_benign' if known_label == 'benign' else 'unknown'
        }
        return jsonify(result)

    data = {}
    if request.is_json:
        data = request.get_json(silent=True) or {}
    else:
        data = request.form.to_dict()
    sample = data.get('sample', '') or data.get('file', '')
    if sample is None or sample == '':
        abort(400, 'No sample provided')
    import re
    if re.fullmatch(r'[0-9a-fA-F]{64}', str(sample)):
        hash_value = str(sample)
        label, score = malware_detector.predict_from_hash(hash_value)
        features = {'sha256': hash_value}
        risk = risk_analyzer.assess(features, score)
        hash_known = label != 'unknown'
    else:
        features = feature_extractor.extract_features(sample)
        hash_value = features.get('sha256')
        known_label, known_score = malware_detector.predict_from_hash(hash_value) if hash_value else ('unknown', 0.0)
        hash_known = known_label != 'unknown'
        if hash_known:
            label, score = known_label, known_score
        else:
            label, score = malware_detector.predict(features)
        risk = risk_analyzer.assess(features, score)
    result = {
        'result': label,
        'score': score,
        'risk': risk,
        'features': features,
        'sha256': hash_value,
        'source': 'text',
        'hash_known': hash_known,
        'hash_status': 'known_malicious' if hash_known and label == 'malicious' else 'known_benign' if hash_known else 'unknown'
    }
    return jsonify(result)


@app.errorhandler(400)
def bad_request(error):
    return jsonify(error=str(error.description)), 400


@app.route('/api/models', methods=['GET'])
def models_info():
    """Retourne des informations sur le modèle ML chargé (si présent)."""
    try:
        from app.services import malware_detector
        info = {
            'model_loaded': bool(getattr(malware_detector, 'MODEL', None)),
            'model_path': getattr(malware_detector, 'MODEL_PATH', None)
        }
    except Exception:
        info = {'model_loaded': False, 'model_path': None}
    return jsonify(info)


@app.route('/api/features', methods=['GET'])
def features_info():
    """Retourne les features agrégées pour un hash donné (query param 'hash').

    Exemple: GET /api/features?hash=<64-hex>
    """
    from flask import request
    h = request.args.get('hash')
    if not h:
        return jsonify(error='missing hash parameter'), 400
    try:
        from app.services import malware_detector
        features = malware_detector.fetch_features_for_hash(h)
        if not features:
            return jsonify(found=False, features={}), 200
        return jsonify(found=True, features=features)
    except Exception as e:
        return jsonify(error=str(e)), 500


def _is_pid_running(pid: int) -> bool:
    """Check whether a process with given PID is running.

    Uses tasklist on Windows and os.kill on Unix-like systems.
    """
    try:
        pid = int(pid)
    except Exception:
        return False
    if os.name == 'nt':
        try:
            # Use tasklist to check for the PID
            p = subprocess.run(['tasklist', '/FI', f'PID eq {pid}'], capture_output=True, text=True)
            out = p.stdout or ''
            return str(pid) in out
        except Exception:
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except Exception:
            return False


@app.route('/api/train', methods=['POST'])
def trigger_training():
    """Start a background training job that runs ml/train.py.

    Security: if environment variable TRAIN_KEY is set, the request must include
    header X-TRAIN-KEY with the same value. If TRAIN_KEY is not set, the endpoint
    is open (use with caution).

    Returns JSON with started:true and pid when the job is launched.
    """
    # Authorization
    env_key = os.environ.get('TRAIN_KEY')
    if env_key:
        header_key = request.headers.get('X-TRAIN-KEY')
        if not header_key or header_key != env_key:
            return jsonify(error='unauthorized'), 403

    train_script = PROJECT_ROOT / 'ml' / 'train.py'
    if not train_script.exists():
        return jsonify(error='train script not found'), 500

    logs_dir = PROJECT_ROOT / 'ml'
    logs_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = logs_dir / 'train_stdout.log'
    stderr_path = logs_dir / 'train_stderr.log'
    pid_path = logs_dir / 'train.pid'
    status_path = logs_dir / 'train_status.json'

    python_exe = sys.executable or 'python'

    # Prepare creationflags for Windows to detach the process
    creationflags = 0
    if hasattr(subprocess, 'CREATE_NEW_PROCESS_GROUP'):
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

    try:
        out = open(stdout_path, 'ab')
        err = open(stderr_path, 'ab')
    except Exception as e:
        return jsonify(error=f'cannot open log files: {e}'), 500

    try:
        proc = subprocess.Popen([python_exe, str(train_script)], cwd=str(PROJECT_ROOT), stdout=out, stderr=err, creationflags=creationflags)
        pid = proc.pid
        # write pid and status
        try:
            pid_path.write_text(str(pid), encoding='utf-8')
        except Exception:
            pass
        status = {'pid': pid, 'started_at': int(time.time()), 'stdout': str(stdout_path), 'stderr': str(stderr_path)}
        try:
            status_path.write_text(json.dumps(status), encoding='utf-8')
        except Exception:
            pass
        return jsonify(started=True, pid=pid, stdout=str(stdout_path), stderr=str(stderr_path))
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route('/api/train/status', methods=['GET'])
def train_status():
    """Return last started training PID and whether it is still running, plus tail of stdout.

    Query params:
      - lines (optional): number of last lines of log to return (default 50)
    """
    pid_path = PROJECT_ROOT / 'ml' / 'train.pid'
    stdout_path = PROJECT_ROOT / 'ml' / 'train_stdout.log'
    if not pid_path.exists():
        return jsonify(running=False, message='no training process recorded'), 200
    try:
        pid = int(pid_path.read_text(encoding='utf-8').strip())
    except Exception:
        return jsonify(running=False, message='invalid pid recorded'), 200

    running = _is_pid_running(pid)

    # read tail of stdout
    lines = int(request.args.get('lines', 50)) if request.args.get('lines') else 50
    tail = []
    try:
        with open(stdout_path, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
            tail = all_lines[-lines:]
    except Exception:
        tail = []

    return jsonify(running=running, pid=pid, log_tail=''.join(tail)), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
