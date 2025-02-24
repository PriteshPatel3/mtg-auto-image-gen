import matplotlib.pyplot as plt
import requests
from PIL import Image
from io import BytesIO
import numpy as np
import cv2

RATE = 2.8
USERNAME = "MICHAEL XYZ"  # Change this to the actual username

def fetch_card_data(api_call):
    """Fetch card data from the API."""
    response = requests.get(api_call)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve data for {api_call} with status code {response.status_code}")
        return None

def fetch_card_image(card_image_url):
    """Fetch the card image from the URL."""
    img_response = requests.get(card_image_url)
    return Image.open(BytesIO(img_response.content))

def display_image_subplot(img, card_name, card_price, index):
    """Display the card image in a subplot with its name and price."""
    plt.subplot(1, 3, (index % 3) + 1)
    plt.imshow(img)
    plt.axis('off')
    plt.text(
        0.5, -0.1, 
        f"{card_name}\nUSD: ${card_price}\nMYR: RM{float(card_price) * RATE:.2f}", 
        fontsize=12, color='white', ha='center', transform=plt.gca().transAxes
    )

def add_title_and_user_info(title_shown):
    """Add title and user information to the plot."""
    if not title_shown:
        plt.suptitle(
            "Pasar Malam MTG", fontsize=16, color='white', 
            ha='left', x=0.1, y=0.98
        )
        plt.figtext(0.1, 0.92, f"User: {USERNAME}", fontsize=12, color='white', ha='left')
        plt.figtext(0.1, 0.88, f"Rate: {RATE}", fontsize=12, color='white', ha='left')
        return True
    return title_shown

def display_card_images(api_calls):
    """Display card images with their names and prices."""
    fig = plt.figure(figsize=(15, 7))  # Create main figure
    title_shown = False  # Track if title has been displayed
    images = [] 

    for i, call in enumerate(api_calls):
        card_data = fetch_card_data(call)
        if card_data and 'prices' in card_data and card_data['prices'].get('usd'):
            card_name = card_data['name']
            card_price = card_data['prices']['usd']
            card_image_url = card_data['image_uris'].get('normal')

            if card_image_url:
                img = fetch_card_image(card_image_url)
                display_image_subplot(img, card_name, card_price, i)

                plt.gcf().set_facecolor('black')  # Set background color to black
                title_shown = add_title_and_user_info(title_shown)

                # If 3 images are filled, save and show the plot
                if (i + 1) % 3 == 0 or i == len(api_calls) - 1:  
                    plt.subplots_adjust(hspace=0.5)
                    plt.gcf().canvas.draw()  # Ensure rendering
                    img_plot = np.array(fig.canvas.renderer.buffer_rgba())
                    images.append(cv2.cvtColor(img_plot, cv2.COLOR_RGBA2BGR))
                    plt.savefig('test.jpg', facecolor='black')  # Save before showing
                    # plt.show()

                    # Start new figure for the next batch of 3
                    fig = plt.figure(figsize=(15, 7))  
                    title_shown = False  # Reset title for next batch

    return images