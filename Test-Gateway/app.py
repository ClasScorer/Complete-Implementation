
import requests
from PIL import Image, ImageDraw, ImageFont
import datetime

# === Configuration ===
api_url = "http://localhost:8000/api/process-frame"  # Update with your backend URL
image_path = "2.jpeg"  # Replace with your image file path

# === Prepare Request Data ===
lecture_id = "lecstring"
timestamp = datetime.datetime.now().isoformat()  # ISO8601 formatted timestamp

# === Send POST Request ===
with open(image_path, "rb") as image_file:
    files = {"image": image_file}
    # Form data fields need to match the expected names: lectureId and timestamp.
    data = {"lectureId": lecture_id, "timestamp": timestamp}
    
    response = requests.post(api_url, files=files, data=data)

# === Handle Response ===
if response.status_code == 200:
    result = response.json()
    print("API Response:", result)
    
    # Open the original image for annotation
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    # Optional: define a font for labels (you may need to adjust the path or font size)
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        font = ImageFont.load_default()
    
    # Loop over each detected face and draw the bounding box and person ID label
    for face in result.get("faces", []):
        bbox = face.get("bounding_box", {})
        x = bbox.get("x", 0)
        y = bbox.get("y", 0)
        width = bbox.get("width", 0)
        height = bbox.get("height", 0)
        
        # Draw rectangle: top-left (x,y) to bottom-right (x+width, y+height)
        draw.rectangle([(x, y), (x + width, y + height)], outline="red", width=3)
        
        # Annotate with person_id (displayed slightly above the bounding box)
        person_id = face.get("person_id", "unknown")
        text_position = (x, max(y - 20, 0))
        draw.text(text_position, person_id, fill="red", font=font)
    
    # Show the annotated image (or save it to a file)
    image.show()
    # To save, uncomment the following line:
    # image.save("annotated_image.jpg")
else:
    print("Error in API request:", response.status_code, response.text)
