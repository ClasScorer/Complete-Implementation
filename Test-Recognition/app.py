import requests
from PIL import Image, ImageDraw, ImageFont
import datetime
import os

# === Configuration ===
api_url = "http://localhost:23121/identify"  # Direct URL to recognition service
image_path = "human_4.jpg"  # Replace with your face image file path

# === Send POST Request ===
with open(image_path, "rb") as image_file:
    files = {
        "image": ("face.jpg", image_file, "image/jpeg")
    }
    
    print(f"Sending request to {api_url}...")
    response = requests.post(api_url, files=files)

# === Handle Response ===
if response.status_code == 200:
    result = response.json()
    print("API Response:", result)
    
    # Open the original image for annotation
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    # Try to load font for text
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        font = ImageFont.load_default()
    
    # Extract recognition information
    person_id = result.get("person_id", "unknown")
    status = result.get("status", "unknown")
    
    # Choose color based on recognition status
    if status == "found":
        color = "green"   # Known person
    elif status == "new":
        color = "blue"    # New person
    else:
        color = "red"     # Error or unknown status
    
    # Draw a border around the image with the appropriate color
    border_width = 5
    draw.rectangle(
        [(0, 0), (image.width - 1, image.height - 1)], 
        outline=color, 
        width=border_width
    )
    
    # Draw recognition information at the top of the image
    status_text = f"Person ID: {person_id} | Status: {status}"
    draw.text((10, 10), status_text, fill=color, font=font)
    
    # Show the annotated image
    image.show()
    
    # To save the image, uncomment the following line:
    # image.save("recognition_demo_result.jpg")
    
    # Print detailed information
    print("\nDetailed Recognition Information:")
    print("=" * 50)
    print(f"Person ID: {person_id}")
    print(f"Status: {status}")
    print("=" * 50)
    
else:
    print("Error in API request:", response.status_code)
    print("Response text:", response.text)

# === Additional functionalities (uncomment to use) ===

# Function to store a new person in the database
def store_person(image_path, person_id):
    store_url = "http://localhost:23121/store"
    with open(image_path, "rb") as image_file:
        files = {"image": ("face.jpg", image_file, "image/jpeg")}
        data = {"person_id": person_id}
        response = requests.post(store_url, files=files, data=data)
    
    if response.status_code == 200:
        print(f"Successfully stored person {person_id}")
        print(response.json())
    else:
        print(f"Error storing person: {response.status_code}")
        print(response.text)

# Uncomment to store a new person
# store_person("new_person.jpg", "new_person_id_123")
