import fastapi
import cv2 as cv
import joblib
import numpy as np
import matplotlib.pyplot as plt
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Form, File, UploadFile
import os
import sklearn
import torch
from torch_models import *
import zipfile

app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/models")
def get_model_names():
    path_sklearn = "models/sklearn"
    path_pytorch = "models/pytorch"

    sklearn_models = set([f.split('.')[0] for f in os.listdir(path_sklearn)])
    pytorch_models = set([f.split('.')[0] for f in os.listdir(path_pytorch)])

    return list(sklearn_models.union(pytorch_models))

def process_img(img):
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    img = cv.bitwise_not(img)
    
    thress = cv.threshold(img, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]
    contour = cv.findContours(thress, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[0]
    x, y, w, h = cv.boundingRect(contour[0])
    img = img[y:y+h, x:x+w]
    img = cv.resize(img, (28, 28), interpolation=cv.INTER_AREA)
    return img

def predict_pytorch(img, model_name):
    from torch import nn

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    path = "models/pytorch/"

    model = name_to_model[model_name]().to(device)
    model.load_state_dict(torch.load(path + model_name + ".pth", map_location=device))
    img_tensor = torch.tensor(img, dtype=torch.float32).unsqueeze(0).unsqueeze(0).to(device) / 255.0

    model.eval()
    with torch.no_grad():
        output = model(img_tensor)
        probabilities = nn.Softmax(dim=1)(output)
        return probabilities.cpu().numpy()

def predict_sklearn(img, model_name):
    try:
        model = joblib.load(f'models/sklearn/{model_name}.pkl')
    except FileNotFoundError:
        # descomprimimos el modelo que estara en .zip
        with zipfile.ZipFile(f'models/sklearn/{model_name}.zip', 'r') as zip_ref:
            zip_ref.extractall(f'models/sklearn/')
        model = joblib.load(f'models/sklearn/{model_name}.pkl')

    img_flattened = img.flatten().reshape(1, -1)
    
    prediction = model.predict_proba(img_flattened)
    return prediction

def predict(img, model_name):
    list_sklearn_models = [model.split(".")[0] for model in os.listdir("models/sklearn")]
    list_pytorch_models = [model.split(".")[0] for model in os.listdir("models/pytorch")]

    prediction = None

    print(f"Model name: {model_name}", flush=True)
    print(f"Sklearn models: {list_sklearn_models}", flush=True)
    print(f"PyTorch models: {list_pytorch_models}", flush=True)

    if model_name in list_sklearn_models:
        prediction = predict_sklearn(img, model_name)
    elif model_name in list_pytorch_models:
        prediction = predict_pytorch(img, model_name)
    else:
        prediction = "Model not found"

    return prediction

@app.post("/content")
def post_content(model_name: str = Form(...), img: UploadFile = File(...)):
    contents = img.file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv.imdecode(nparr, cv.IMREAD_COLOR)
    img = process_img(img)

    prediction = predict(img, model_name)
    prediction = (prediction * 100).tolist()

    return {"prediction": prediction}