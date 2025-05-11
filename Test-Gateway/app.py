import requests
from PIL import Image, ImageDraw, ImageFont
import datetime
import streamlit as st
import cv2
import numpy as np
import time
import io
import threading
import queue

# === Configuration ===
api_url = "http://localhost:8000/api/process-frame"
lecture_id = "lecstring"

def process_image(image_data, is_file=True):
    """Process an image through the API and return the annotated image"""
    timestamp = datetime.datetime.now().isoformat()
    
    if is_file:
        # For file upload
        files = {"image": image_data}
    else:
        # For webcam frame (convert numpy array to file-like object)
        is_success, buffer = cv2.imencode(".jpg", image_data)
        if not is_success:
            st.error("Failed to encode image")
            return None
        image_bytes = io.BytesIO(buffer.tobytes())
        files = {"image": ("frame.jpg", image_bytes, "image/jpeg")}
    
    # Form data
    data = {"lectureId": lecture_id, "timestamp": timestamp}
    
    try:
        # Send POST request
        response = requests.post(api_url, files=files, data=data)
        

        
        if response.status_code == 200:
            result = response.json()
            
            # Open the image for annotation
            if is_file:
                # For file upload
                image = Image.open(image_data)
            else:
                # For webcam frame
                image = Image.fromarray(cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB))
            
            draw = ImageDraw.Draw(image)
            
            # Try to load font
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except IOError:
                font = ImageFont.load_default()
            
            # Draw bounding boxes and labels
            for face in result.get("faces", []):
                bbox = face.get("bounding_box", {})
                x = bbox.get("x", 0)
                y = bbox.get("y", 0)
                width = bbox.get("width", 0)
                height = bbox.get("height", 0)
                
                # Draw rectangle
                draw.rectangle([(x, y), (x + width, y + height)], outline="red", width=3)
                
                # Get status information
                person_id = face.get("person_id", "unknown")
                attention = face.get("attention_status", "UNKNOWN")
                hand_raised = "✋" if face.get("hand_raising_status", {}).get("is_hand_raised", False) else ""
                
                # Combine information for display
                display_text = f"{person_id} ({attention}) {hand_raised}"
                
                # Annotate with text slightly above the bounding box
                text_position = (x, max(y - 20, 0))
                draw.text(text_position, display_text, fill="red", font=font)
            
            # Add summary
            summary = result.get("summary", {})
            summary_text = [
                f"Total faces: {result.get('total_faces', 0)}",
                f"Known faces: {summary.get('known_faces', 0)}",
                f"New faces: {summary.get('new_faces', 0)}",
                f"Focused: {summary.get('focused_faces', 0)}",
                f"Unfocused: {summary.get('unfocused_faces', 0)}",
                f"Hands raised: {summary.get('hands_raised', 0)}"
            ]
            
            # Draw summary at the top of the image
            y_pos = 10
            for line in summary_text:
                draw.text((10, y_pos), line, fill="blue", font=font)
                y_pos += 20
                
            return image, result
        else:
            st.error(f"Error in API request: {response.status_code} - {response.text}")
            return None, None
    
    except Exception as e:
        st.error(f"Exception during API request: {str(e)}")
        return None, None

# Create a thread-safe queue for frame processing
if "frame_queue" not in st.session_state:
    st.session_state.frame_queue = queue.Queue(maxsize=30)  # Limit queue size

def webcam_capture(stop_event, frame_queue):
    """Capture frames from webcam and put them in the queue"""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return
    
    try:
        while not stop_event.is_set():
            success, frame = cap.read()
            if not success:
                break
                
            # If queue is full, remove oldest frame
            if frame_queue.full():
                try:
                    frame_queue.get_nowait()
                except queue.Empty:
                    pass
                    
            # Put new frame in queue
            try:
                frame_queue.put((time.time(), frame), block=False)
            except queue.Full:
                pass
                
            # Short sleep to prevent high CPU usage
            time.sleep(0.03)  # ~30 FPS capture
    finally:
        cap.release()

def process_frames():
    """Process frames from the queue in the main thread"""
    if "webcam_running" not in st.session_state or not st.session_state.webcam_running:
        return
        
    frame_placeholder = st.empty()
    status_placeholder = st.empty()
    last_process_time = 0
    process_interval = 1.0  # Process every 1 second
    
    try:
        # Get the latest frame from the queue
        if not st.session_state.frame_queue.empty():
            timestamp, frame = st.session_state.frame_queue.get()
            
            # Always display the current frame (smooth display)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)
            
            # Process frame at specified interval
            current_time = time.time()
            if current_time - last_process_time >= process_interval:
                status_placeholder.text("Processing frame...")
                processed_image, result = process_image(frame, is_file=False)
                
                if processed_image is not None:
                    # Convert PIL Image back to numpy array for display
                    processed_array = np.array(processed_image)
                    frame_placeholder.image(processed_array, channels="RGB", use_column_width=True)
                    
                    if result:
                        status_placeholder.json(result)
                    else:
                        status_placeholder.text("No detection results")
                
                last_process_time = current_time
    except Exception as e:
        st.error(f"Error processing frames: {str(e)}")

def main():
    st.title("Face Detection Gateway Tester")
    
    # Sidebar configuration
    st.sidebar.header("Settings")
    
    # Initialize session state for webcam
    if 'webcam_running' not in st.session_state:
        st.session_state.webcam_running = False
        st.session_state.stop_event = threading.Event()
        
    # Input method selection
    input_method = st.sidebar.radio("Select input method:", ["Upload Image", "Webcam"])
    
    if input_method == "Upload Image":
        # Stop webcam if it's running
        if st.session_state.webcam_running:
            st.session_state.stop_event.set()
            st.session_state.webcam_running = False
            st.rerun()
            
        # Image upload
        uploaded_file = st.file_uploader("Upload an image:", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            # Display original image
            st.subheader("Original Image")
            image = Image.open(uploaded_file)
            st.image(image, use_column_width=True)
            
            # Process button
            if st.button("Process Image"):
                with st.spinner("Processing..."):
                    # Reset file pointer to beginning
                    uploaded_file.seek(0)
                    
                    # Process image
                    processed_image, result = process_image(uploaded_file)
                    
                    if processed_image is not None:
                        # Display processed image
                        st.subheader("Processed Image")
                        st.image(processed_image, use_column_width=True)
                        
                        # Display JSON result
                        st.subheader("API Response")
                        st.json(result)
    
    else:  # Webcam input
        st.subheader("Webcam Stream")
        
        # Start/stop webcam button
        if not st.session_state.webcam_running:
            if st.button("Start Webcam"):
                # Reset stop event
                st.session_state.stop_event = threading.Event()
                
                # Clear the frame queue
                st.session_state.frame_queue = queue.Queue(maxsize=30)
                
                # Start webcam thread
                st.session_state.webcam_running = True
                thread = threading.Thread(
                    target=webcam_capture,
                    args=(st.session_state.stop_event, st.session_state.frame_queue)
                )
                thread.daemon = True
                thread.start()
                st.rerun()
        else:
            if st.button("Stop Webcam"):
                st.session_state.stop_event.set()
                st.session_state.webcam_running = False
                st.rerun()
                
            # Process frames in the main thread
            process_frames()
        
        # Warning about webcam usage
        st.info("Note: Processing happens at 1 FPS to avoid overwhelming the API, while display remains smooth.")

if __name__ == "__main__":
    main()
