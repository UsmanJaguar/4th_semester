import os
import io
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Try to import face_recognition; if unavailable, fall back to OpenCV Haar cascades
try:
    import face_recognition
    USING_FACE_REC = True
except Exception:
    USING_FACE_REC = False
    import cv2


def load_reference_encodings(reference_dir):
    """Load reference data.

    If `face_recognition` is available, returns (encodings, names).
    Otherwise returns (templates, names) where templates are grayscale face images.
    """
    items = []
    names = []
    if not os.path.isdir(reference_dir):
        return items, names

    for fname in os.listdir(reference_dir):
        path = os.path.join(reference_dir, fname)
        if not os.path.isfile(path):
            continue
        name = os.path.splitext(fname)[0]
        try:
            if USING_FACE_REC:
                image = face_recognition.load_image_file(path)
                encs = face_recognition.face_encodings(image)
                if len(encs) > 0:
                    items.append(encs[0])
                    names.append(name)
            else:
                # load with OpenCV and try to detect a face region to use as template
                img = cv2.imread(path)
                if img is None:
                    continue
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))
                if len(faces) > 0:
                    x, y, w, h = faces[0]
                    face_tpl = gray[y:y+h, x:x+w]
                else:
                    # fallback: use the whole image as template
                    face_tpl = cv2.resize(gray, (200, 200))

                items.append(face_tpl)
                names.append(name)
        except Exception:
            continue

    return items, names


def annotate_image_and_save(image_np, face_locations, face_names, out_path):
    """Draw rectangles and labels on image (numpy array), save to out_path."""
    pil_image = Image.fromarray(image_np)
    draw = ImageDraw.Draw(pil_image)

    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except Exception:
        font = ImageFont.load_default()

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        draw.rectangle(((left, top), (right, bottom)), outline=(0, 255, 0), width=3)
        # compute text size in a forward-compatible way
        try:
            text_width, text_height = font.getsize(name)
        except Exception:
            try:
                bbox = draw.textbbox((0, 0), name, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            except Exception:
                # fallback values
                text_width, text_height = (len(name) * 6, 12)

        draw.rectangle(((left, bottom - text_height - 6), (left + text_width + 6, bottom)), fill=(0, 255, 0))
        draw.text((left + 3, bottom - text_height - 3), name, fill=(0, 0, 0), font=font)

    pil_image.save(out_path)


def process_image_file(file_storage, known_items, known_names, out_path, tolerance=0.5):
    """Process uploaded file. If `face_recognition` available, do recognition.

    Otherwise use OpenCV Haar cascade for detection and template matching for recognition.

    Returns list of dicts: {'name': name, 'box': [top,right,bottom,left], 'distance': score}
    """
    # Read uploaded bytes
    file_storage.seek(0)
    data = file_storage.read()
    if USING_FACE_REC:
        # face_recognition can accept file-like objects
        try:
            image = face_recognition.load_image_file(io.BytesIO(data))
        except Exception:
            # fallback to numpy decoding
            import cv2
            nparr = np.frombuffer(data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        results = []
        face_names = []

        for encoding, loc in zip(face_encodings, face_locations):
            name = 'Unknown'
            distance = None
            if known_items:
                distances = face_recognition.face_distance(known_items, encoding)
                best_idx = int(np.argmin(distances))
                distance = float(distances[best_idx])
                if distance <= tolerance:
                    name = known_names[best_idx]

            face_names.append(name)
            results.append({'name': name, 'box': [int(x) for x in loc], 'distance': distance})

        annotate_image_and_save(image, face_locations, face_names, out_path)
        return results
    else:
        import cv2
        # decode image
        nparr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError('Could not decode image')
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        rects = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        face_locations = []
        face_names = []
        results = []

        for (x, y, w, h) in rects:
            top, right, bottom, left = y, x + w, y + h, x
            face_locations.append((top, right, bottom, left))

            name = 'Unknown'
            score = None
            if known_items:
                roi = gray[y:y+h, x:x+w]
                if roi.size == 0:
                    match_val = 0.0
                else:
                    best_val = -1.0
                    for tpl in known_items:
                        try:
                            tpl_resized = cv2.resize(tpl, (w, h))
                        except Exception:
                            tpl_resized = cv2.resize(tpl, (w, h), interpolation=cv2.INTER_AREA)
                        # use template matching
                        res = cv2.matchTemplate(roi, tpl_resized, cv2.TM_CCOEFF_NORMED)
                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                        if max_val > best_val:
                            best_val = max_val
                    match_val = float(best_val)

                score = match_val
                if match_val >= 0.5:
                    # pick the best name
                    best_idx = 0
                    best_score = -1.0
                    for idx, tpl in enumerate(known_items):
                        tpl_resized = cv2.resize(tpl, (w, h))
                        res = cv2.matchTemplate(roi, tpl_resized, cv2.TM_CCOEFF_NORMED)
                        _, max_val, _, _ = cv2.minMaxLoc(res)
                        if max_val > best_score:
                            best_score = max_val
                            best_idx = idx
                    name = known_names[best_idx]

            face_names.append(name)
            results.append({'name': name, 'box': [int(top), int(right), int(bottom), int(left)], 'distance': score})

        annotate_image_and_save(rgb, face_locations, face_names, out_path)
        return results
