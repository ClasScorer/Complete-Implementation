import requests
import os
import json
import base64
from PIL import Image, ImageDraw, ImageFont
import io

# === Configuration ===
api_url = "http://localhost:23120"  # Base URL to localization service
image_path = "2.jpeg"  # Replace with your test image file path

# === Send POST Request to Localize Image ===
def localize_image(image_path):
    print(f"Sending image to {api_url}/localize-image/...")
    
    with open(image_path, "rb") as image_file:
        files = {
            "file": ("image.jpg", image_file, "image/jpeg")
        }
        response = requests.post(f"{api_url}/localize-image/", files=files)
    
    if response.status_code == 200:
        result = response.json()
        print("\nAPI Response from localize-image:")
        print(json.dumps(result, indent=2))
        print(f"\nDetected {result['detected_humans']} humans in the image.")
        return result
    else:
        print(f"Error in API request: {response.status_code}")
        print(f"Response text: {response.text}")
        return None

# === Get Bounding Box Coordinates ===
def get_bounding_boxes():
    print(f"\nFetching bounding box coordinates from {api_url}/localize-coords...")
    
    response = requests.get(f"{api_url}/localize-coords")
    
    if response.status_code == 200:
        result = response.json()
        print("\nAPI Response from localize-coords:")
        print(json.dumps(result, indent=2))
        return result["bounding_boxes"]
    else:
        print(f"Error in API request: {response.status_code}")
        print(f"Response text: {response.text}")
        return []

# === Get Cropped Images ===
def get_cropped_images():
    print(f"\nFetching cropped images from {api_url}/localized-image...")
    
    response = requests.get(f"{api_url}/localized-image")
    
    if response.status_code == 200:
        result = response.json()
        print("\nReceived cropped images:")
        for i, img_data in enumerate(result["images"]):
            print(f"  - {img_data['name']}")
        return result["images"]
    else:
        print(f"Error in API request: {response.status_code}")
        print(f"Response text: {response.text}")
        return []

# === Download ZIP file of cropped images ===
def download_zip():
    print(f"\nDownloading ZIP file from {api_url}/download-zip...")
    
    response = requests.get(f"{api_url}/download-zip", stream=True)
    
    if response.status_code == 200:
        # Get filename from content-disposition header or use default
        content_disposition = response.headers.get('content-disposition', '')
        filename = 'humans.zip'
        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[1].strip('"')
        
        # Save the file
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Successfully downloaded and saved as {filename}")
        return filename
    else:
        print(f"Error in API request: {response.status_code}")
        print(f"Response text: {response.text}")
        return None

# === Draw bounding boxes on original image ===
def visualize_results(image_path, bounding_boxes):
    # Open the original image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    
    # Try to load font for text
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        font = ImageFont.load_default()
    
    # Draw each bounding box
    for bbox in bounding_boxes:
        x_min = bbox["x_min"]
        y_min = bbox["y_min"]
        x_max = bbox["x_max"]
        y_max = bbox["y_max"]
        
        # Draw rectangle
        draw.rectangle(
            [(x_min, y_min), (x_max, y_max)], 
            outline="green", 
            width=3
        )
        
        # Draw label
        label_text = f"Human #{bbox['human_id']} ({bbox['score']})"
        draw.text((x_min, y_min - 20), label_text, fill="green", font=font)
    
    # Show the annotated image
    image.show()
    
    # Save the annotated image
    output_path = "annotated_" + os.path.basename(image_path)
    image.save(output_path)
    print(f"\nAnnotated image saved as {output_path}")
    return output_path

# === Save base64 images to disk ===
def save_cropped_images(images_data):
    os.makedirs("cropped", exist_ok=True)
    
    saved_paths = []
    for img_data in images_data:
        # Decode base64 image
        image_bytes = base64.b64decode(img_data["image"])
        image = Image.open(io.BytesIO(image_bytes))
        
        # Save image
        output_path = os.path.join("cropped", img_data["name"])
        image.save(output_path)
        saved_paths.append(output_path)
        print(f"Saved {output_path}")
    
    return saved_paths

# === Run the complete test ===
def run_test():
    # Check if the service is up
    try:
        health_response = requests.get(f"{api_url}/health")
        if health_response.status_code == 200:
            print("Localization service is healthy!")
            print(health_response.json())
        else:
            print("Service health check failed. Is the service running?")
            return
    except requests.exceptions.ConnectionError:
        print(f"Cannot connect to {api_url}. Is the service running?")
        return
    
    # 1. Localize image (upload and process)
    localization_result = localize_image(image_path)
    if not localization_result:
        return
    
    # 2. Get bounding box coordinates
    bounding_boxes = get_bounding_boxes()
    if bounding_boxes:
        # Visualize the results on the original image
        visualize_results(image_path, bounding_boxes)
    
    # 3. Get cropped images in base64 format
    cropped_images = get_cropped_images()
    if cropped_images:
        # Save the cropped images
        save_cropped_images(cropped_images)
    
    # 4. Download ZIP file
    download_zip()

if __name__ == "__main__":
    run_test()