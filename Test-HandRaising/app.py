import requests
from PIL import Image, ImageDraw, ImageFont
import datetime
import os
import io
import base64

# === Configuration ===
api_url = "http://localhost:23122/detect-hand-raising"  # Direct URL to handraising service
image_path = "human_4.jpg"  # Replace with your image file path

# === Prepare Request Data ===
timestamp = datetime.datetime.now().isoformat()  # ISO8601 formatted timestamp
student_id = "student_demo_123"  # Demo student ID

# === Send POST Request ===
print(f"Sending request to {api_url}...")
with open(image_path, "rb") as image_file:
    files = {
        "file": ("image.jpg", image_file, "image/jpeg"),
        "student_id": (None, student_id),
        "timestamp": (None, timestamp)
    }
    
    response = requests.post(api_url, files=files)

# === Handle Response ===
if response.status_code == 200:
    result = response.json()
    print(f"Hand-raising detection results:")
    print(f"Is hand raised: {result.get('is_hand_raised', False)}")
    print(f"Confidence: {result.get('confidence', 0.0)}")
    
    if result.get('hand_position'):
        print(f"Hand position: x={result['hand_position'].get('x', 0)}, y={result['hand_position'].get('y', 0)}")
    
    # Open the original image for annotation
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    # Try to load font for text
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        font = ImageFont.load_default()
    
    # Add annotation based on hand raising status
    is_hand_raised = result.get("is_hand_raised", False)
    confidence = result.get("confidence", 0.0)
    
    # Draw a status indicator at the top of the image
    status_text = f"Hand raised: {is_hand_raised} | Confidence: {confidence:.2f}"
    color = "green" if is_hand_raised else "red"
    draw.text((10, 10), status_text, fill=color, font=font)
    
    # If hand position is available, draw a marker at that position
    hand_position = result.get("hand_position")
    if hand_position and is_hand_raised:
        hand_x = hand_position.get("x", 0)
        hand_y = hand_position.get("y", 0)
        
        # Draw a circle at the hand position
        circle_radius = 10
        draw.ellipse(
            [(hand_x - circle_radius, hand_y - circle_radius), 
             (hand_x + circle_radius, hand_y + circle_radius)], 
            fill="yellow", outline="black", width=2
        )
        
        # Draw a line connecting hand position text to the circle
        draw.text((hand_x + 15, hand_y - 15), "Hand", fill="blue", font=font)
    
    # Save the annotated image
    output_path = "hand_raising_direct_demo_output.jpg"
    image.save(output_path)
    print(f"Annotated image saved to: {output_path}")
    
    # Show the annotated image 
    image.show()
    
else:
    print("Error in API request:", response.status_code)
    print("Response text:", response.text)
