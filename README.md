# 🛡️ Malware Detector — Machine Learning Malware Detection Platform

<p align="center">

**An intelligent malware detection platform combining Machine Learning, static feature extraction and a Flask REST API.**

Detect • Analyze • Classify • Monitor

</p>

---

## 📌 Overview

**Malware Detector** is a lightweight cybersecurity platform designed to detect potentially malicious software and samples using **Machine Learning**.

The project combines:

- 🧠 Machine Learning classification
- 🔬 Static feature extraction
- 🌐 Flask REST API
- 🗄️ SQLite-based local training database
- 🌲 Random Forest classification
- 📊 Risk analysis and detection scoring
- 🔐 Optional authentication for sensitive operations
- 🧪 Automated testing with `pytest`
- 📈 Training and evaluation utilities
- 🖥️ Web-based frontend served by Flask

The architecture is intentionally modular so that individual components — feature extraction, classification, risk analysis, database handling and API routes — can be independently extended or replaced.

> ⚠️ **Security Notice:** This project is intended for cybersecurity research, malware-analysis experimentation and educational purposes. Never execute unknown malware samples directly on your primary operating system or production infrastructure.

---

## ✨ Key Features

| Feature                | Description                                               |
| ---------------------- | --------------------------------------------------------- |
| 🧠 ML Detection        | Classifies samples using a trained Machine Learning model |
| 🌲 Random Forest       | Default classification algorithm                          |
| 🔬 Feature Extraction  | Extracts numerical/static characteristics from samples    |
| 🎯 Risk Scoring        | Converts detection results into a risk assessment         |
| 🔎 Hash Analysis       | Allows analysis based on SHA-256 hashes                   |
| 📁 File Scanning       | Supports file uploads through the REST API                |
| 🌐 REST API            | Flask-based API for programmatic integration              |
| 🏋️ Model Training      | Training can be triggered through the API                 |
| 📊 Model Evaluation    | Accuracy and classification reports                       |
| 🗄️ SQLite Dataset      | Local database generation for ML training                 |
| 📝 Logging             | Training jobs generate stdout/stderr/status information   |
| 🔐 Training Protection | Optional `TRAIN_KEY` authentication                       |
| 🧪 Testing             | Unit tests using `pytest`                                 |
| 🖥️ Web Interface       | Static frontend served through Flask                      |

---

# 🏗️ Architecture

The application follows a modular pipeline:

```text
                         ┌─────────────────────┐
                         │     Client / UI     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     Flask API       │
                         │      app/app.py     │
                         └──────────┬──────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  │                 │                 │
                  ▼                 ▼                 ▼
          ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
          │    Feature   │  │    Malware   │  │     Risk     │
          │   Extractor  │  │   Detector   │  │   Analyzer   │
          └──────┬───────┘  └──────┬───────┘  └──────────────┘
                 │                 │
                 │                 ▼
                 │        ┌──────────────────┐
                 │        │ ML Model         │
                 │        │ Random Forest    │
                 │        └──────────────────┘
                 │
                 ▼
          ┌─────────────────┐
          │ Feature Dataset │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │ SQLite / SQL    │
          │ Training Data   │
          └─────────────────┘
```

---

# 🔄 Detection Workflow

A typical malware-analysis request follows this workflow:

```text
📁 Sample / Hash
       │
       ▼
🔬 Feature Extraction
       │
       ▼
📐 Feature Vector
       │
       ▼
🧠 ML Model
       │
       ▼
🎯 Prediction
       │
       ▼
📊 Detection Score
       │
       ▼
⚠️ Risk Analysis
       │
       ▼
📦 JSON API Response
```

The system separates **feature extraction**, **classification** and **risk analysis** so that the Machine Learning layer can evolve independently from the API.

---

# 📂 Project Structure

```text
Malware-Detector/
│
├── app/
│   ├── app.py
│   │
│   ├── routes/
│   │   ├── scan.py
│   │   ├── dashboard.py
│   │   └── auth.py
│   │
│   ├── services/
│   │   ├── feature_extractor.py
│   │   ├── malware_detector.py
│   │   └── risk_analyzer.py
│   │
│   └── models/
│       ├── User.py
│       ├── Scan.py
│       ├── Feature.py
│       └── Malware.py
│
├── ml/
│   ├── preprocess.py
│   ├── train.py
│   ├── evaluate.py
│   │
│   ├── models/
│   │   └── random_forest.pkl
│   │
│   └── data.db
│
├── database/
│   └── schema.sql
│
├── data/
│   └── datasets/
│
├── tests/
│   └── ...
│
├── static/
│   └── ...
│
├── running items/
│   ├── requirements.txt
│   └── ...
│
├── .gitignore
├── README.md
└── LICENSE
```

### 📦 Main Components

### `app/`

Contains the Flask application and application-layer logic.

- `app.py` — Flask entry point
- `routes/` — REST API endpoints
- `services/` — detection and analysis logic
- `models/` — application/domain models

### `ml/`

Contains the Machine Learning pipeline.

- `preprocess.py` — preprocessing and feature preparation
- `train.py` — model training
- `evaluate.py` — evaluation utilities
- `models/` — persisted trained models

### `database/`

Contains the original SQL schema and training-data source.

### `tests/`

Contains automated tests for application and ML components.

### `static/`

Contains the frontend assets served by Flask.

---

# 🧠 Machine Learning Pipeline

The ML subsystem is divided into several stages.

## 1️⃣ Dataset Preparation

`ml/train.py` reads the SQL schema and relevant data from:

```text
database/schema.sql
```

It can construct a local SQLite database:

```text
ml/data.db
```

This design allows local training without requiring a permanent MySQL/MariaDB server.

---

## 2️⃣ Preprocessing

Raw data is transformed into a numerical representation suitable for Machine Learning.

The preprocessing layer is responsible for tasks such as:

- Data cleaning
- Feature selection
- Numerical conversion
- Aggregation
- Missing-value handling
- Dataset preparation

---

## 3️⃣ Training

The default classifier is:

```text
RandomForestClassifier
```

The training pipeline performs:

```text
Dataset
   ↓
Preprocessing
   ↓
Feature Matrix
   ↓
Train/Test Split
   ↓
Random Forest
   ↓
Evaluation
   ↓
Model Serialization
```

The trained model is persisted under:

```text
ml/models/random_forest.pkl
```

---

## 4️⃣ Evaluation

`ml/evaluate.py` provides utilities for evaluating the classifier.

Typical evaluation metrics include:

- Accuracy
- Precision
- Recall
- F1-score
- Classification report

For a cybersecurity classifier, **accuracy alone should not be considered sufficient**. False negatives can be particularly important because a malicious sample incorrectly classified as benign may represent a security risk.

---

# 🎯 Detection & Risk Analysis

The detection service is responsible for loading the trained model and generating predictions.

The main service is:

```text
app/services/malware_detector.py
```

It exposes functionality conceptually equivalent to:

```python
predict(features)
predict_from_hash(hash)
```

The risk-analysis layer then interprets the prediction and produces a higher-level security assessment.

A typical result can contain:

```json
{
  "result": "malware",
  "score": 0.94,
  "risk": "high",
  "sha256": "...",
  "features": {}
}
```

> The exact response depends on the implementation and currently loaded model.

---

# 🌐 REST API

The application exposes a Flask REST API.

Base URL:

```text
http://localhost:5000
```

---

## 🔍 `POST /api/scan`

Scans a sample and returns a detection result.

### File upload

```bash
curl -F "file=@/path/to/sample.exe" \
     http://localhost:5000/api/scan
```

### JSON request

```bash
curl -X POST \
     http://localhost:5000/api/scan \
     -H "Content-Type: application/json" \
     -d "{\"sample\":\"0123456789abcdef...\"}"
```

Possible response structure:

```json
{
  "result": "malware",
  "score": 0.91,
  "risk": "high",
  "sha256": "..."
}
```

---

## 🤖 `GET /api/models`

Returns information about the currently loaded model.

Example:

```bash
curl http://localhost:5000/api/models
```

Possible response:

```json
{
  "model_loaded": true,
  "model_path": "ml/models/random_forest.pkl"
}
```

---

## 🔬 `GET /api/features`

Retrieves aggregated features associated with a hash.

Example:

```bash
curl "http://localhost:5000/api/features?hash=<SHA256>"
```

---

## 🏋️ `POST /api/train`

Starts a Machine Learning training job.

```bash
curl -X POST http://localhost:5000/api/train
```

If `TRAIN_KEY` is configured:

```bash
curl -X POST \
     http://localhost:5000/api/train \
     -H "X-TRAIN-KEY: YOUR_TRAIN_KEY"
```

A successful response may contain:

```json
{
  "started": true,
  "pid": 12345,
  "stdout": "ml/train_stdout.log",
  "stderr": "ml/train_stderr.log"
}
```

---

## 📡 `GET /api/train/status`

Returns the status of the latest training job.

```bash
curl http://localhost:5000/api/train/status
```

This can provide information such as:

- Process ID
- Running state
- Training logs
- Job status

---

# ⚙️ Installation

## 📋 Requirements

- Python **3.8+**
- `pip`
- Git
- Virtual environment recommended

The project is designed to remain relatively lightweight and avoids unnecessary top-level dependencies.

---

## 🐍 1. Clone the repository

```bash
git clone https://github.com/<YOUR_USERNAME>/<REPOSITORY>.git
cd <REPOSITORY>
```

---

## 🔧 2. Create a virtual environment

### Windows

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 📦 3. Install dependencies

```bash
pip install -r "running items/requirements.txt"
```

Expected dependencies include packages such as:

```text
Flask
scikit-learn
joblib
numpy
xgboost
pytest
```

The exact dependency set is defined by:

```text
running items/requirements.txt
```

---

# 🚀 Running the Application

From the project root:

```bash
python app\app.py
```

The Flask development server is expected to listen on:

```text
http://localhost:5000
```

Alternatively:

```bash
python -m app.app
```

if the project packaging supports module execution.

---

# 🏋️ Training the Model

The ML training script can be executed independently:

```bash
python ml/train.py
```

The training process can:

1. Read the SQL dataset
2. Build the local SQLite database
3. Prepare the feature matrix
4. Split the dataset
5. Train the classifier
6. Evaluate the model
7. Serialize the trained model

The resulting model is stored in:

```text
ml/models/random_forest.pkl
```

---

# 🧪 Testing

Run the complete test suite:

```bash
pytest -q
```

For more verbose output:

```bash
pytest -v
```

Testing should be extended whenever a new detection rule, feature extractor, API endpoint or ML component is introduced.

---

# 📊 Model Development

For reproducible experimentation, the recommended workflow is:

```text
📥 Dataset
   ↓
🧹 Preprocessing
   ↓
🔬 Feature Engineering
   ↓
✂️ Train/Test Split
   ↓
🧠 Model Training
   ↓
📊 Evaluation
   ↓
💾 Model Serialization
   ↓
🔌 API Integration
```

When comparing models, consider evaluating:

- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix
- False-positive rate
- False-negative rate
- Inference latency

For malware detection specifically, **recall and false-negative analysis are particularly important**.

---

# 🔐 Security Considerations

This project deals with potentially malicious data, therefore deployment requires additional security controls.

## Training endpoint

The training endpoint can be protected with:

```text
TRAIN_KEY
```

For example:

```powershell
$env:TRAIN_KEY="your-secret-key"
```

The API then expects:

```text
X-TRAIN-KEY: your-secret-key
```

### ⚠️ Production recommendations

Do not expose the development Flask server directly to the public Internet.

For production environments, consider:

- Reverse proxy
- HTTPS/TLS
- Strong authentication
- Rate limiting
- Request-size limits
- Input validation
- Structured logging
- Process isolation
- Containerization
- Network segmentation
- Secret management
- Restricted filesystem permissions
- Malware-sample sandboxing

---

# 🧪 Malware Sample Safety

If the project is used with real malware:

### ❌ Do not

- Execute unknown samples on your personal machine
- Open suspicious executables directly
- Upload confidential samples to public services
- Store malware alongside sensitive personal files
- Run analysis with unnecessary administrator privileges

### ✅ Prefer

- Isolated virtual machines
- Disposable analysis environments
- Network isolation
- Snapshots
- Dedicated test datasets
- Sandboxed execution environments
- Restricted permissions

The current project primarily focuses on **static/ML-based analysis** and should not be considered a complete malware sandbox.

---

# 📝 Logging & Observability

Training jobs generate operational files under `ml/`:

```text
ml/
├── train_stdout.log
├── train_stderr.log
├── train.pid
└── train_status.json
```

These files provide basic observability into asynchronous training jobs.

For production deployments, a more robust logging architecture could use:

- Python `logging`
- JSON structured logs
- Log rotation
- Centralized log collection
- Metrics
- Health checks
- Monitoring dashboards

---

# 🗄️ Database Architecture

The project uses two complementary data concepts:

### Source SQL

```text
database/schema.sql
```

This represents the original SQL-based dataset/schema.

### Local ML database

```text
ml/data.db
```

This SQLite database is generated for local ML processing.

This separation allows the training process to remain relatively independent from an external database server.

---

# 🔌 Extensibility

The architecture allows individual components to be replaced without rewriting the complete application.

Possible extensions include:

### 🧠 Machine Learning

- XGBoost
- Gradient Boosting
- SVM
- Logistic Regression
- Neural Networks
- Ensemble classifiers
- Scikit-learn pipelines

### 🔬 Feature Engineering

Possible future features include:

- PE header characteristics
- Section statistics
- Import/export information
- Entropy
- String characteristics
- File metadata
- Opcode-derived features
- API-call statistics
- Behavioral indicators

### 🌐 API

Potential additions:

- Authentication
- API keys
- Rate limiting
- OpenAPI/Swagger documentation
- Versioned endpoints
- Async job queues

---

# 🗺️ Roadmap

## 🔹 Current

- [x] Flask REST API
- [x] File/hash scanning
- [x] Feature extraction layer
- [x] Random Forest model
- [x] Model persistence
- [x] SQLite training database
- [x] Training endpoint
- [x] Training status endpoint
- [x] Basic automated tests
- [x] Risk analysis service

## 🔹 Planned

- [ ] 📊 Advanced model evaluation dashboard
- [ ] 🧠 Automated model comparison
- [ ] 🔬 Advanced PE feature extraction
- [ ] 📈 ROC-AUC / PR-AUC evaluation
- [ ] 🧪 Expanded test coverage
- [ ] 🔐 Complete API authentication
- [ ] 📚 OpenAPI documentation
- [ ] 🐳 Docker deployment
- [ ] ⚙️ CI/CD pipeline
- [ ] 📊 Model monitoring
- [ ] 🔄 Automated model versioning
- [ ] 🧬 Feature importance visualization
- [ ] 🛡️ Dedicated malware sandbox integration

---

# 🤝 Contributing

Contributions are welcome.

A typical contribution workflow:

```bash
git checkout -b feature/my-feature
```

Implement your changes, then:

```bash
git add .
git commit -m "feat: add my feature"
git push origin feature/my-feature
```

Then open a Pull Request.

### Contribution guidelines

Please:

- Keep modules focused and maintainable
- Add tests for critical functionality
- Document public API changes
- Avoid committing secrets
- Avoid committing generated datasets unnecessarily
- Follow the existing project structure
- Explain significant ML changes
- Include evaluation results when changing the model

---

# 🚫 Files That Should Generally Not Be Committed

Consider adding generated or sensitive files to `.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]

# Virtual environments
.venv/
venv/
env/

# Environment variables
.env
.env.*

# ML generated files
ml/data.db
ml/train_stdout.log
ml/train_stderr.log
ml/train.pid
ml/train_status.json

# Python tooling
.pytest_cache/
.mypy_cache/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

> ⚠️ If `random_forest.pkl` is required to run the application immediately, decide explicitly whether it should be version-controlled or downloaded/generated during setup. Large models should generally be handled through a model registry or artifact-storage solution.

---

# 🧩 Development Philosophy

The project follows several principles:

### 🧱 Modularity

Application, ML and data-processing components remain separated.

### 🔍 Auditability

The codebase aims to keep the detection pipeline understandable and inspectable.

### ⚡ Lightweight execution

The project avoids unnecessary dependencies where practical.

### 🔄 Reproducibility

Training scripts and explicit dependencies make experiments easier to reproduce.

### 🔐 Security by design

Sensitive operations such as model training should be protected before production deployment.

---

# 📚 Technical Stack

| Layer               | Technology                      |
| ------------------- | ------------------------------- |
| Backend             | 🐍 Python                       |
| Web Framework       | 🌐 Flask                        |
| Machine Learning    | 🧠 Scikit-learn                 |
| Default Model       | 🌲 Random Forest                |
| Additional ML       | ⚡ XGBoost                      |
| Numerical Computing | 🔢 NumPy                        |
| Model Serialization | 📦 Joblib                       |
| Database            | 🗄️ SQLite                       |
| Source SQL          | 🐬 MySQL/MariaDB-compatible SQL |
| Testing             | 🧪 Pytest                       |
| Frontend            | 🖥️ HTML/CSS/JavaScript          |
| API Format          | 🔗 REST / JSON                  |

---

# 📈 Future Production Architecture

A more mature deployment could evolve toward:

```text
                     ┌─────────────────┐
                     │    Web Client   │
                     └────────┬────────┘
                              │ HTTPS
                              ▼
                     ┌─────────────────┐
                     │ Reverse Proxy   │
                     │ Nginx / Proxy   │
                     └────────┬────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │   Flask API     │
                     └────────┬────────┘
                              │
               ┌──────────────┼──────────────┐
               ▼              ▼              ▼
        ┌────────────┐ ┌────────────┐ ┌────────────┐
        │ Detection  │ │ Risk       │ │ Auth       │
        │ Service    │ │ Analyzer   │ │ Service    │
        └─────┬──────┘ └────────────┘ └────────────┘
              │
              ▼
        ┌──────────────┐
        │ Model        │
        │ Registry     │
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │ ML Pipeline  │
        └──────┬───────┘
               │
               ▼
        ┌──────────────┐
        │ Dataset / DB │
        └──────────────┘
```

This architecture would make the platform easier to scale, monitor and operate securely.

---

# ⚖️ Disclaimer

This software is provided for **educational, research and authorized cybersecurity analysis purposes**.

The authors and contributors are not responsible for damage, data loss, system compromise or misuse resulting from the software.

Only analyze files, systems and datasets for which you have appropriate authorization.

---

# 📄 License

No explicit license is currently included in the repository.

Before distributing or using the project commercially, add an appropriate `LICENSE` file and verify the licensing requirements of:

- Source datasets
- Third-party libraries
- Pre-trained models
- Generated model artifacts
- External APIs

---

# 👨‍💻 Development Status

**Project status:** 🚧 Active Development

The architecture is functional but remains extensible. ML performance, feature engineering, API security, automated testing and production deployment can all be further improved.

---

# ⭐ Support the Project

If this project is useful for your cybersecurity or Machine Learning research:

⭐ Star the repository
🐛 Report bugs through Issues
💡 Suggest improvements
🔀 Submit Pull Requests
📚 Improve the documentation

---

<p align="center">

**🛡️ Malware Detector**

_Machine Learning • Cybersecurity • Threat Detection_

</p>
