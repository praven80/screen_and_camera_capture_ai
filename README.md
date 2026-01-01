# Screen & Cam Capture Studio

A Streamlit-based application for recording screen and camera footage with real-time video analysis powered by AWS Bedrock.

You can view a short demo video in the "Demo" folder.

## Features

- **Screen Recording**: Capture your screen activity
- **Camera Recording**: Record from your webcam
- **Video Analysis**: AI-powered insights using AWS Bedrock
- **Customizable Duration**: Record from 5 to 60 seconds
- **Real-time Progress**: Live preview and progress tracking
- **Video Format Support**: Automatic conversion to H.264 format
- **High-Quality Output**: Configurable FPS and resolution

## Prerequisites

- Python 3.8+
- Webcam (for camera recording)
- AWS Account with Bedrock access
- FFmpeg installed on your system

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd screen-cam-capture-studio
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure AWS credentials:
```bash
aws configure
```

## Dependencies

```
streamlit
opencv-python
numpy
boto3
pyautogui
Pillow
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Select recording duration using the slider (5-60 seconds)

3. Choose recording type:
   - Click "Record Screen" to capture screen activity
   - Click "Record Camera" to capture webcam footage

4. After recording:
   - Preview the recorded video
   - Enter a prompt for video analysis
   - Click "Extract Insights" for AI-powered analysis

5. Use "Clear Recording" to remove the current recording

## Features in Detail

### Screen Recording
- Captures full screen at 15 FPS
- Automatic frame synchronization
- Temporary storage management
- H.264 video encoding

### Camera Recording
- 640x480 resolution
- Real-time preview
- Custom FPS settings
- Automatic format conversion

### Video Analysis
- Powered by AWS Bedrock
- Custom prompt support
- Detailed content analysis
- Quick processing time

## File Structure

```
.
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── recorded_videos/       # Storage for recorded videos
└── README.md             # Project documentation
```

## Configuration

Key configurations in `app.py`:
```python
fps = 15  # Target FPS for recordings
resolution = (640, 480)  # Camera resolution
video_format = 'mp4v'  # Video codec
```

## AWS Integration

The application uses:
- AWS Bedrock for video analysis
- AWS SDK (boto3) for AWS services interaction
- Region configuration for AWS services

## Security

- Temporary file handling
- Automatic cleanup
- Secure AWS credentials management

## Performance

- Optimized frame capture
- Efficient video encoding
- Memory-conscious operations
- Real-time processing