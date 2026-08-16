# Train a RandomForest model from the SQL dump (schema.sql) without pandas.
# This script extracts the CREATE TABLE for `malware_data`, imports a limited
# number of tuples from the INSERT statement to a local SQLite DB (ml/data.db),
# then trains a RandomForest on the numeric columns and saves the model to
# ml/models/random_forest.pkl.

import re
import sqlite3
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = PROJECT_ROOT / 'database' / 'schema.sql'
DB_PATH = PROJECT_ROOT / 'ml' / 'data.db'
MODELS_DIR = PROJECT_ROOT / 'ml' / 'models'
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Tunables
MAX_ROWS_TO_IMPORT = 10000  # limit how many tuples to import from the big INSERT for speed (increased per request)
RANDOM_STATE = 42


def _clean_create_statement(create_sql: str) -> str:
    s = create_sql
    s = s.replace('`', '"')
    s = re.sub(r"\)\s*ENGINE=.*?;", ");", s, flags=re.IGNORECASE | re.S)
    s = re.sub(r"\)\s*DEFAULT CHARSET=.*?;", ");", s, flags=re.IGNORECASE | re.S)
    s = re.sub(r"COLLATE\s+[^;\n]*", "", s, flags=re.IGNORECASE)
    return s


def _extract_tuples(values_text: str, max_tuples: int):
    """Parse the VALUES part (which contains many parenthesized tuples separated by commas).
    Return a list of tuple substrings including their enclosing parentheses.
    This parser counts parentheses and is robust to embedded commas.
    """
    tuples = []
    i = 0
    n = len(values_text)
    while i < n and len(tuples) < max_tuples:
        # find next '(' that starts a tuple
        while i < n and values_text[i] != '(':
            i += 1
        if i >= n:
            break
        depth = 0
        start = i
        while i < n:
            if values_text[i] == '(':
                depth += 1
            elif values_text[i] == ')':
                depth -= 1
                if depth == 0:
                    # include the closing ')'
                    i += 1
                    break
            i += 1
        tuple_str = values_text[start:i].strip()
        if tuple_str:
            tuples.append(tuple_str)
 
        while i < n and values_text[i] in ',\r\n \t':
            i += 1
    return tuples


def build_sqlite_db(sql_path: Path, db_path: Path, max_rows: int = MAX_ROWS_TO_IMPORT):
    """Build a SQLite DB by extracting CREATE TABLE and collecting tuples from
    all INSERT INTO malware_data blocks across the SQL dump until max_rows is
    reached.
    """
    if db_path.exists():
        print(f"SQLite DB already exists at {db_path}, skipping import.")
        return

    text = sql_path.read_text(encoding='utf-8', errors='ignore')

    m = re.search(r"CREATE TABLE\s+`?malware_data`?\s*\((.*?)\)\s*;", text, flags=re.S | re.I)
    if not m:
        raise RuntimeError("Could not find CREATE TABLE malware_data in schema.sql")

    create_stmt = m.group(0)
    create_stmt = _clean_create_statement(create_stmt)

    insert_iter = re.finditer(r"INSERT INTO\s+`?malware_data`?[^;]*;", text, flags=re.S | re.I)
    all_tuples = []
    total_blocks = 0
    for ins in insert_iter:
        total_blocks += 1
        block = ins.group(0)
        parts = block.split('VALUES', 1)
        if len(parts) < 2:
            continue
        values_part = parts[1].strip()
        if values_part.endswith(';'):
            values_part = values_part[:-1]
        tuples = _extract_tuples(values_part, max_rows - len(all_tuples))
        if tuples:
            all_tuples.extend(tuples)
        if len(all_tuples) >= max_rows:
            break

    if not all_tuples:
        raise RuntimeError('No tuples parsed from any INSERT block for malware_data')

    inserted = len(all_tuples)
    insert_clean = 'INSERT INTO malware_data VALUES ' + ',\n'.join(all_tuples) + ';'

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    try:
        cur.executescript(create_stmt)
        cur.executescript(insert_clean)
        conn.commit()
    finally:
        cur.close()
        conn.close()
    print(f"Imported {inserted} rows into {db_path} (from {total_blocks} INSERT blocks)")


def train_from_db(db_path: Path, model_path: Path):
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute('SELECT * FROM malware_data LIMIT 1')
    cols = [d[0] for d in cur.description]

    # Read rows
    cur.execute('SELECT * FROM malware_data')
    rows = cur.fetchall()
    conn.close()

    if not rows:
        raise RuntimeError('No rows in malware_data')

    # Convert rows to numeric feature matrix
    drop_cols = set(['hash', 'classification', 'millisecond'])
    feature_cols = [c for c in cols if c not in drop_cols]

    X = []
    y = []
    for r in rows:
        rowd = dict(zip(cols, r))
        cls = rowd.get('classification', None)
        if cls is None:
            continue
        y.append(1 if str(cls).lower() == 'malware' else 0)
        feat = []
        for c in feature_cols:
            v = rowd.get(c)
            try:
                fv = float(v) if v is not None else 0.0
            except Exception:
                fv = 0.0
            feat.append(fv)
        X.append(feat)

    X = np.array(X)
    y = np.array(y)

    if X.shape[0] < 2:
        raise RuntimeError('Not enough data to train')

    from sklearn.model_selection import train_test_split

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y if len(set(y))>1 else None)

    clf = RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE)
    clf.fit(X_train, y_train)

    try:
        clf.feature_names_in_ = np.array(feature_cols)
    except Exception:
        pass

    acc = None
    if X_test.shape[0] > 0 and len(set(y)) > 1:
        acc = clf.score(X_test, y_test)
    print(f"Trained RandomForest. Test accuracy: {acc}")

    joblib.dump(clf, str(model_path))
    print(f"Saved model to {model_path}")


if __name__ == '__main__':
    print('Building sqlite DB (ml/data.db) from database/schema.sql (limited rows)...')
    build_sqlite_db(SQL_PATH, DB_PATH, max_rows=MAX_ROWS_TO_IMPORT)
    print('Training model from DB...')
    model_target = MODELS_DIR / 'random_forest.pkl'
    train_from_db(DB_PATH, model_target)
    print('Done.')
