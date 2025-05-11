import random
from moviepy.editor import ImageClip, concatenate_videoclips, vfx, AudioFileClip, CompositeVideoClip
import numpy as np
import cv2
import textwrap
import os

class VideoGenerator:
    def _get_images(self, images_path):
        images = []
        for file in os.listdir(images_path):
            if file.endswith(".png"):
                images.append(f"{images_path}/{file}")
        return images
        
    def _get_audio(self, audio_files_path):
        audio_files = []
        for file in os.listdir(audio_files_path):
            if file.endswith(".mp3"):
                audio_files.append(f"{audio_files_path}/{file}")
        return audio_files[0]
        
    def _get_audio_length(self, file_path):
        with AudioFileClip(file_path) as audio:
            return audio.duration  # Duration in seconds
        
    def _create_text_overlay(self, text, video_width, video_height, output_path, max_line_length=20):
        overlay = np.zeros((video_height, video_width, 4), dtype=np.uint8)

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2.5
        font_thickness = 5
        text_color = (255, 255, 255, 255)

        lines = textwrap.wrap(text, width=max_line_length)

        text_height = 0
        for line in lines:
            text_size = cv2.getTextSize(line, font, font_scale, font_thickness)[0]
            text_height += text_size[1] + 10

        y = (video_height - text_height) // 2

        for line in lines:
            text_size = cv2.getTextSize(line, font, font_scale, font_thickness)[0]
            x = (video_width - text_size[0]) // 2
            cv2.putText(overlay, line, (x, y), font, font_scale, text_color, font_thickness, cv2.LINE_AA)
            y += text_size[1] + 10

        overlay_path = os.path.join(output_path, "text_overlay.png")
        cv2.imwrite(overlay_path, overlay)

        return overlay_path

    def _create_crumbling_transition(self, clip, duration_per_image):
        """Simulate paper crumbling transition."""
        # Here you could add a crumbling effect. As an example, we'll just do a quick scale-up and fade.
        crumbling_clip = clip.resize(lambda t: 1 + 0.1 * t)  # Simulating crumbling with zoom-out
        crumbling_clip = crumbling_clip.fx(vfx.fadein, duration=duration_per_image * 0.3)
        crumbling_clip = crumbling_clip.fx(vfx.fadeout, duration=duration_per_image * 0.7)
        return crumbling_clip

    def generate_video(self, input_text, images_path, audio_files_path, output_path, output_file_name):
        image_files = self._get_images(images_path)
        music_path = self._get_audio(audio_files_path)

        audio_duration = self._get_audio_length(music_path)

        total_video_duration = min(20, audio_duration)

        num_images = len(image_files)
        duration_per_image = total_video_duration / num_images

        video_width, video_height = 1080, 1920

        clips = []
        for idx, image_file in enumerate(image_files):

            clip = ImageClip(image_file, duration=duration_per_image)

            # Resize and crop the image to fill the screen without distortion
            clip = clip.resize(height=video_height)
            if clip.w < video_width:
                clip = clip.resize(width=video_width)

            clip = clip.crop(x_center=clip.w / 2, y_center=clip.h / 2, width=video_width, height=video_height)

            # Apply a center crop to ensure the image fully fits the screen
            if idx == 0:
                clip = self._create_crumbling_transition(clip, duration_per_image)
                
                # Add text overlay (only for the first image)
                text_overlay_path = self._create_text_overlay(input_text, video_width, video_height, output_path)
                text_overlay = ImageClip(text_overlay_path, duration=duration_per_image * 0.6)
                text_overlay = text_overlay.set_position(('center', 'center'))
                text_overlay = text_overlay.crossfadeout(duration_per_image * 0.3)

                clip = CompositeVideoClip([clip, text_overlay])
            else:
                clip = clip.fx(vfx.fadein, duration=0.5)  # Smooth fade-in transition for subsequent images

            clips.append(clip)

        # Concatenate all clips to create the final video
        final_clip = concatenate_videoclips(clips, method="compose")

        # Add background music
        background_music = AudioFileClip(music_path).subclip(0, total_video_duration)
        final_clip = final_clip.set_audio(background_music)

        # Export the final video
        final_clip.write_videofile(os.path.join(output_path, output_file_name), fps=24)

