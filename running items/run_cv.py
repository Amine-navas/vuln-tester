import sys
sys.path.insert(0, r'C:\Users\VIET\Downloads\Malware-Detector-machine-learning-AI-main')
from app.services import feature_extractor, malware_detector
p = r'C:\Users\VIET\Downloads\Malware-Detector-machine-learning-AI-main\temp_cv.txt'
with open(p, 'r', encoding='utf-8') as f:
    text = f.read()
features = feature_extractor.extract_features(text)
print('FEATURES=', features)
print('PRED=', malware_detector.predict(features))
