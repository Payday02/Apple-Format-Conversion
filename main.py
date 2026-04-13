import os
import subprocess
import time
from moviepy import VideoFileClip
from PIL import Image
import pillow_heif

input_folder = "input"
output_folder = "output"

def strip_metadata(input_file, output_file):
    try:
        command = [
            'ffmpeg',
            '-i', input_file,
            '-map_metadata', '-1',  # Remove all metadata
            '-metadata:s:v', 'rotate=0',  # Reset rotation metadata
            '-c:v', 'libx264',  # Re-encode video to H.264
            '-c:a', 'aac',  # Re-encode audio to AAC
            '-crf', '23',  # Control video quality (lower is better)
            '-preset', 'fast',  # Use a faster encoding preset
            output_file
        ]
        subprocess.run(command, check=True)
        print(f"Metadata stripped and file re-encoded successfully: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running FFmpeg: {e}")

def convert_mov_to_mp4(input_folder, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Process all .mov files in the input folder
    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith('.mov'):  # Process only .mov files
            input_path = os.path.join(input_folder, file_name)
            output_file_name = os.path.splitext(file_name)[0] + ".mp4"  # Change extension to .mp4
            output_path = os.path.join(output_folder, output_file_name)

            print(f"Processing file: {input_path}")

            try:
                # Temporary file for metadata-stripped .mov
                temp_file = os.path.join(output_folder, "temp_file.mov")
                
                if os.path.exists(temp_file):
                    os.remove(temp_file)

                # Strip metadata and re-encode
                strip_metadata(input_path, temp_file)

                # Check if the temporary file was created
                if not os.path.exists(temp_file):
                    raise FileNotFoundError(f"Temporary file '{temp_file}' not created. Metadata stripping may have failed.")
                
                # Load the metadata-stripped .mov file
                video_clip = VideoFileClip(temp_file)

                # Write the video file to .mp4 format
                video_clip.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    ffmpeg_params=['-preset', 'fast', '-crf', '23', '-threads', '4']
                )

                # Clean up the temporary file
                video_clip.close()
                time.sleep(2)
                os.remove(temp_file)


                print(f"Successfully converted: {input_path} -> {output_path}")

            except Exception as e:
                print(f"An error occurred while processing {file_name}: {e}")
                
def convert_heic_to_png(input_folder, output_folder):
    # loop through all files in the directory
    for filename in os.listdir(input_folder):
        # check if the file is in HEIC format
        if filename.lower().endswith(".heic"):
            # create an Image object from the HEIC file
            filepath = os.path.join(input_folder, filename)
            print("Converting:", filepath)
            heif_file = pillow_heif.read_heif(filepath)
            image = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
            )

            # create a new filename for the PNG file
            new_filename = os.path.splitext(filename)[0] + ".png"
            new_filepath = os.path.join(output_folder, new_filename)

            image.save(new_filepath, format("png"))

try:
    print("Starting HEIC stage")
    convert_heic_to_png(input_folder, output_folder)
    print("Starting MOV stage")
    convert_mov_to_mp4(input_folder, output_folder)
    print("Process Completed Successfully!")
except Exception as e:
    print(f"An error occurred: {str(e)}")