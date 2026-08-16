# Malware-Detector-machine-learning-AI

Ce dépôt contient du code et des notebooks pour la détection de malwares (ML). Ce scaffold ajoute une UI statique minimale et un backend Flask léger pour servir la page et un endpoint de démonstration.

Prérequis:
- Python 3.8+
- pip

Installation et exécution:

```bash
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt
# Start the app as a package (so imports work):
python -m app.app
```

Ouvrir ensuite http://localhost:5000 dans un navigateur.

Arrêter le serveur (PowerShell) :

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\stop-all.ps1
```

Notes:
- L'API /api/scan accepte désormais soit un texte, soit un fichier uploadé via multipart/form-data.
- Le moteur extrait des indicateurs de risque à partir du contenu (taille, nombre de lignes, présence de mots-clés suspects, extension de fichier, etc.) et renvoie un verdict + niveau de risque.
