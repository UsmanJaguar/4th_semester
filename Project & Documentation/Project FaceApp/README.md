# Face Detection & Recognition (Flask)

Project scaffold that detects faces in uploaded images and recognizes faces from a `reference/` folder.

Project structure

```
face_detection_project/
│── app.py
│── requirements.txt
│── README.md
│
│── reference/         # Put your face images here (e.g. my_face.jpg)
│
│── templates/
│     └── index.html
│
│── static/
│     ├── styles.css
│     └── processed/
│
│── utils/
      └── face_utils.py
```

Quick setup (Windows, recommended: Anaconda/Miniconda)

1. Create and activate environment (recommended):

```powershell
conda create -n faceapp python=3.9 -y; conda activate faceapp
```

2. Install system dependencies (Windows often needs `dlib`):

Recommended: install dlib from conda-forge first to avoid build issues:

```powershell
conda install -c conda-forge dlib -y
pip install -r requirements.txt
```

If you cannot install `dlib`, an alternative is to run this project inside WSL or a Linux server.

3. Add a reference image

Place one or more photos of your face into the `reference/` folder. Filenames are used as the label (e.g. `Chusm.jpg` → label `Chusm`).

4. Run the app

```powershell
python app.py
# then open http://127.0.0.1:5000
```

How it works

- On startup the server loads face encodings from all images in `reference/`.
- Upload an image through the web UI. The server detects face locations, computes encodings, and compares them to the known encodings.
- The processed image with drawn boxes and labels is saved to `static/processed/` and displayed back in the UI.

Notes & troubleshooting

- Windows: installing `dlib`/`face_recognition` can be painful; using `conda` or WSL is strongly recommended.
- If detection finds multiple faces, each face will be labeled with the best match or `Unknown`.
- Tweak tolerance in `utils/face_utils.py` (default 0.5) for stricter/looser matching.
