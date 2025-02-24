from fastapi import FastAPI, Request, Form, File, UploadFile, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd
import io
import base64
import cv2
from module.functions import display_card_images
import numpy as np
app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 Templates
templates = Jinja2Templates(directory="templates")

def convert_cv2_to_base64(image: np.ndarray) -> str:
    """Convert OpenCV image (NumPy array) to Base64."""
    _, buffer = cv2.imencode(".jpg", image)
    base64_str = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/jpeg;base64,{base64_str}"

@app.get("/")
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "data": None})

@app.post("/upload/")
async def upload_csv(request: Request, file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        return templates.TemplateResponse("index.html", {"request": request, "error": "Only CSV files are allowed!", "data": None})
    
    # Read CSV
    content = await file.read()
    df = pd.read_csv(io.StringIO(content.decode("utf-8")))

    # Convert first 5 rows to dictionary
    data ={}
    data['df'] = df.to_dict(orient="records")
    df = pd.read_csv('test_data.csv')
    card_names = df['Name'].tolist()
    set_codes = df['Set code'].tolist()
    foils = df['Foil'].tolist()
    api_calls = [
        f"https://api.scryfall.com/cards/named?exact={name}&set={set_code}&is={foil}&game=paper"
        for name, set_code, foil in zip(card_names, set_codes, foils)
    ]
    images = display_card_images(api_calls)  
    base64_imgs = [convert_cv2_to_base64(image) for image in images]
    []
    data['images'] = base64_imgs
    print(data)
    return templates.TemplateResponse("index.html", {"request": request, "data": data})
