import requests
from PIL import Image, ImageDraw, ImageFont
import datetime
import os

# === Configuration ===
api_url = "http://localhost:23123/detect-face-attention"  # Direct URL to attention service
image_path = "human_5.jpg"  # Replace with your face image file path

# === Prepare Request Data ===
face_id = "student_demo_123"  # Demo student ID
lecture_id = "lecture_demo_456"  # Demo lecture ID
timestamp = datetime.datetime.now().isoformat()  # ISO8601 formatted timestamp

# === Send POST Request ===
with open(image_path, "rb") as image_file:
    files = {
        "file": ("face.jpg", image_file, "image/jpeg")
    }
    data = {
        "face_id": face_id,
        "lecture_id": lecture_id,
        "timestamp": timestamp
    }
    
    print(f"Sending request to {api_url}...")
    response = requests.post(api_url, files=files, data=data)

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
    
    # Add annotation based on attention status
    attention_status = result.get("attention_status", "UNKNOWN")
    confidence = result.get("confidence", 0.0)
    
    # Draw status text at the top of the image
    status_text = f"Attention: {attention_status} | Confidence: {confidence:.2f}"
    
    # Choose color based on attention status
    if attention_status == "FOCUSED":
        color = "green"
    elif attention_status == "UNFOCUSED":
        color = "red"
    else:
        color = "yellow"
    
    # Draw text at the top of the image
    draw.text((10, 10), status_text, fill=color, font=font)
    
    # Draw a border around the image with the appropriate color
    border_width = 5
    draw.rectangle(
        [(0, 0), (image.width - 1, image.height - 1)], 
        outline=color, 
        width=border_width
    )
    
    # Show the annotated image
    image.show()
    
    # To save the image, uncomment the following line:
    # image.save("attention_demo_result.jpg")
    
    # Print detailed information about the attention detection
    print("\nDetailed Attention Information:")
    print("=" * 50)
    print(f"Face ID: {result.get('face_id', 'N/A')}")
    print(f"Attention Status: {attention_status}")
    print(f"Confidence: {confidence:.4f}")
    print("=" * 50)
    
else:
    print("Error in API request:", response.status_code)
    print("Response text:", response.text)
