from flask import Flask, request, render_template, jsonify, send_file, flash, redirect, url_for, render_template_string
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
import tempfile
import os
import logging

app = Flask(__name__)
app.secret_key = 'hedhWEFESAawe_32e2rfer'  # Change this to a secure random key

# Configure logging
logging.basicConfig(level=logging.INFO)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Your existing download function (slightly modified for better integration)
@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('video_url')
    if not url:
        return jsonify({'error': 'Please enter a video URL.'}), 400

    app.logger.info(f"Received video URL: {url}")

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts = {
                'ffmpeg_location': r'C:\ffmpeg\ffmpeg-7.1.1-essentials_build\bin',
                'format': 'best',
                'outtmpl': 'downloads/%(title).80s.%(ext)s',
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                app.logger.info(f"Downloaded video to: {filename}")

                return send_file(
                    filename,
                    mimetype='video/mp4',
                    as_attachment=True,
                    download_name=os.path.basename(filename)
                )

    except DownloadError as e:
        app.logger.error(f"DownloadError: {e}")
        return jsonify({'error': 'Could not download video. Please check the link.'}), 400
    except Exception as e:
        app.logger.exception("Unexpected error")
        return jsonify({'error': 'An error occurred. Please try again later.'}), 500

# New route for extracting video information without downloading
@app.route('/api/extract', methods=['POST'])
def extract_info():
    data = request.get_json()
    url = data.get('video_url')
    
    if not url:
        return jsonify({'error': 'Please enter a video URL.'}), 400

    app.logger.info(f"Extracting info for URL: {url}")

    try:
        ydl_opts = {
            'ffmpeg_location': r'C:\ffmpeg\ffmpeg-7.1.1-essentials_build\bin',
            'format': 'best',
            'quiet': True,  # Reduce output for info extraction
            'no_warnings': True,
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            # Extract info without downloading
            info = ydl.extract_info(url, download=False)
            
            # Extract relevant information
            video_info = {
                'title': info.get('title', 'Unknown Title'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'upload_date': info.get('upload_date', ''),
                'description': info.get('description', '')[:200] + '...' if info.get('description') else '',
                'webpage_url': info.get('webpage_url', url),
            }
            
            app.logger.info(f"Successfully extracted info for: {video_info['title']}")
            return jsonify(video_info)

    except DownloadError as e:
        app.logger.error(f"DownloadError during info extraction: {e}")
        return jsonify({'error': f'Could not extract video information. Please check the link.'}), 400
    except Exception as e:
        app.logger.exception("Unexpected error during info extraction")
        return jsonify({'error': 'An error occurred while extracting video information.'}), 500

# Serve the main HTML page
# @app.route('/')
# def index():
#     # Read the HTML content from your artifact
#     html_content = """
#     <!-- Your complete HTML content from the artifact goes here -->
#     <!-- This is a placeholder - you'll need to copy the full HTML from the artifact -->
#     """
#     return render_template_string(html_content)

# Handle different platform routes
@app.route('/<platform>')
def platform_page(platform):
    if platform in ['tiktok', 'instagram', 'facebook', 'twitter', 'other']:
        # Same HTML but with JavaScript to show the specific platform page
        html_content = """
        <!-- Same HTML content with additional script to show the platform page -->
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            showPage('""" + platform + """');
        });
        </script>
        """
        return render_template_string(html_content)
    else:
        return redirect(url_for('index'))

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Video downloader is running'})

if __name__ == '__main__':
    # Ensure downloads directory exists
    os.makedirs('downloads', exist_ok=True)
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)