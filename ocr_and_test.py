import sys
from PIL import Image

def main():
    path = r'C:\Users\VIET\AppData\Roaming\Code\agentSessionData\112387d3-22c6-4a3f-812b-e54f202c0521\attachments\1a1c53f6-92b2-404e-9c7b-e54f202c0521\Pasted Image.jpe'
    try:
        img = Image.open(path)
    except Exception as e:
        print('ERROR_OPENING_IMAGE:', e)
        sys.exit(0)

    text = ''
    try:
        import pytesseract
        try:
            text = pytesseract.image_to_string(img, lang='fra')
        except Exception:
            try:
                text = pytesseract.image_to_string(img)
            except Exception as e:
                text = '__OCR_ERROR__:'+str(e)
    except Exception:
        print('NO_PYTESSERACT')
        sys.exit(0)

    print('---OCR_START---')
    print(text)
    print('---OCR_END---')

    sys.path.insert(0, r'C:\Users\VIET\Downloads\Malware-Detector-machine-learning-AI-main')
    from app.services import feature_extractor, malware_detector
    f = feature_extractor.extract_features(text)
    print('FEATURES=', f)
    print('PRED=', malware_detector.predict(f))


if __name__ == '__main__':
    main()
