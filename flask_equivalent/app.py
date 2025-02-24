from flask import Flask, request, render_template
import pandas as pd
import io
import base64
import cv2
from module.functions import display_card_images
import numpy as np

app = Flask(__name__)

def convert_cv2_to_base64(image: np.ndarray) -> str:
    """Convert OpenCV image (NumPy array) to Base64."""
    _, buffer = cv2.imencode(".jpg", image)
    base64_str = base64.b64encode(buffer).decode("utf-8")
    return f"data:image/jpeg;base64,{base64_str}"

@app.route("/", methods=["GET"])
def homepage():
    return render_template("index.html", error=None, data=None)

@app.route("/upload/", methods=["POST"])
def upload_csv():
    file = request.files['file']
    if not file.filename.endswith(".csv"):
        return render_template("index.html", error="Only CSV files are allowed!", data=None)

    # Read CSV
    content = file.read()
    df = pd.read_csv(io.StringIO(content.decode("utf-8")))

    # Convert first 5 rows to dictionary
    data = {}
    data['df'] = df.to_dict(orient="records")
    # df = pd.read_csv('test_data.csv')
    card_names = df['Name'].tolist()
    set_codes = df['Set code'].tolist()
    foils = df['Foil'].tolist()
    api_calls = [
        f"https://api.scryfall.com/cards/named?exact={name}&set={set_code}&is={foil}&game=paper"
        for name, set_code, foil in zip(card_names, set_codes, foils)
    ]
    images = display_card_images(api_calls)  
    base64_imgs = [convert_cv2_to_base64(image) for image in images]
    data['images'] = base64_imgs
    print(data)
    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)