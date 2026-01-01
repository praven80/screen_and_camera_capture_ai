import streamlit as st
import cv2
import numpy as np
import boto3
import json
import base64
import pyautogui
import time
import os
from PIL import Image
import tempfile
import shutil

def record_camera(duration=10, progress_bar=None):
    frames = []
    start_time = time.time()
    fps = 15  # Target FPS
    save_dir = "recorded_videos"
    os.makedirs(save_dir, exist_ok=True)
    
    # Add custom CSS for centering and caption styling
    st.markdown("""
        <style>
        .stImage {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
        }
        .stImage > img {
            max-width: 640px !important;
            width: 100% !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Create empty columns for centering
    _, center_col, _ = st.columns([1, 2, 1])
    
    with center_col:
        # Create a container for both timer and feed
        with st.container():
            # Create placeholders for timer and feed
            timer_placeholder = st.empty()
            live_feed = st.empty()

    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Could not open camera")
            return None
        
        # Set resolution to 640x480
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        frame_count = 0
        while (time.time() - start_time) < duration:
            current_time = time.time()
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
                frame_count += 1
                
                # Display timer with left alignment
                remaining_time = duration - (time.time() - start_time)
                
                # Display live feed
                live_feed.image(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                    channels="RGB",
                    width=640
                )
                
                if progress_bar:
                    progress_bar.progress(min((time.time() - start_time) / duration, 1.0))
                    
            time.sleep(max(0, 1/fps - (time.time() - current_time)))

        cap.release()
        live_feed.empty()
        timer_placeholder.empty()

        if frames:
            height, width = frames[0].shape[:2]
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            output_filename = os.path.join(save_dir, f"camera_recording_{timestamp}.mp4")
            
            # Calculate actual FPS
            actual_fps = frame_count / duration
            
            # Write frames to video file
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_filename, fourcc, actual_fps, (width, height))
            
            for frame in frames:
                out.write(frame)
            out.release()

            # Convert to H.264 format
            temp_output = output_filename.replace('.mp4', '_temp.mp4')
            ffmpeg_command = (
                f'ffmpeg -i "{output_filename}" '
                f'-c:v libx264 -r {actual_fps} '
                f'-pix_fmt yuv420p -preset ultrafast '
                f'-y "{temp_output}"'
            )
            os.system(ffmpeg_command)

            # Replace original file with converted file
            if os.path.exists(temp_output):
                os.remove(output_filename)
                os.rename(temp_output, output_filename)

            return output_filename

    except Exception as e:
        st.error(f"Recording error: {str(e)}")
        return None
    finally:
        if 'cap' in locals() and cap.isOpened():
            cap.release()

def record_screen(duration=10, progress_bar=None):
    frames = []
    timestamps = []
    start_time = time.time()
    fps = 15
    save_dir = "recorded_videos"
    os.makedirs(save_dir, exist_ok=True)

    try:
        while (time.time() - start_time) < duration:
            current_time = time.time()
            frame = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
            frames.append(frame)
            timestamps.append(time.time() - start_time)

            if progress_bar:
                progress_bar.progress(min((time.time() - start_time) / duration, 1.0))
            time.sleep(max(0, 1/fps - (time.time() - current_time)))

        if frames:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            output_filename = os.path.join(save_dir, f"screen_recording_{timestamp}.mp4")
            temp_dir = tempfile.mkdtemp()

            for i, frame in enumerate(frames):
                cv2.imwrite(os.path.join(temp_dir, f'frame_{i:04d}.jpg'), frame)

            os.system(f'ffmpeg -framerate {len(frames)/duration} -i "{os.path.join(temp_dir, "frame_%04d.jpg")}" '
                     f'-c:v libx264 -pix_fmt yuv420p -vf "fps={len(frames)/duration}" -t {duration} '
                     f'-preset ultrafast -y "{output_filename}"')

            shutil.rmtree(temp_dir)
            return output_filename

    except Exception as e:
        st.error(f"Recording error: {str(e)}")
        return None

def analyze_video(video_file, prompt):
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    video_base64 = base64.b64encode(video_file.read()).decode("utf-8")
    
    request = {
        "schemaVersion": "messages-v1",
        "messages": [{
            "role": "user",
            "content": [
                {"video": {"format": "mp4", "source": {"bytes": video_base64}}},
                {"text": prompt}
            ]
        }],
        "system": [{"text": "You are an expert media analyst. Analyze the video based on the user's prompt"}],
        "inferenceConfig": {"max_new_tokens": 300, "top_p": 0.1, "top_k": 20, "temperature": 0.3}
    }

    response = client.invoke_model(modelId="us.amazon.nova-pro-v1:0", body=json.dumps(request))
    return json.loads(response["body"].read())["output"]["message"]["content"][0]["text"]

def main():
    st.title("Screen & Cam Capture Studio")

    if 'video_path' not in st.session_state:
        st.session_state.video_path = None
        st.session_state.recording_complete = False

    # Add duration slider
    duration = st.slider("Recording Duration (seconds)", 
                        min_value=5, 
                        max_value=60, 
                        value=10, 
                        step=5,
                        help="Choose how long you want to record (5-60 seconds)")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"Record Screen ({duration}s)"):
            with st.spinner("Recording screen..."):
                st.session_state.video_path = record_screen(duration=duration, progress_bar=st.progress(0))
                st.session_state.recording_complete = bool(st.session_state.video_path)
                st.rerun()

    with col2:
        if st.button(f"Record Camera ({duration}s)"):
            with st.spinner("Recording from camera..."):
                st.session_state.video_path = record_camera(duration=duration, progress_bar=st.progress(0))
                st.session_state.recording_complete = bool(st.session_state.video_path)
                st.rerun()

    with col3:
        if st.button("Clear Recording"):
            if st.session_state.video_path:
                os.remove(st.session_state.video_path)
                st.session_state.video_path = None
            if st.session_state.recording_complete:
                st.session_state.recording_complete = False    
            st.rerun()

    if st.session_state.recording_complete and st.session_state.video_path:
        try:
            with open(st.session_state.video_path, 'rb') as video_file:
                st.video(video_file.read())
                
                cap = cv2.VideoCapture(st.session_state.video_path)
                if cap.isOpened():
                    fps = cap.get(cv2.CAP_PROP_FPS)
                    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    # st.write(f"Video Info - Duration: {frames/fps:.2f}s, FPS: {fps}, Frames: {frames}")
                cap.release()

                prompt = st.text_input("Enter your prompt for video analysis:", "Explain the video content.")
                if st.button("Extract Insights"):
                    with st.spinner("Extracting insights from video..."):
                        video_file.seek(0)
                        st.write("Insights Generated:", analyze_video(video_file, prompt))

        except Exception as e:
            st.error(f"Error: {str(e)}")
        
if __name__ == "__main__":
    main()