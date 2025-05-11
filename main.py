import os, re, random, sys
from helpers.prompts import Prompts
from helpers.hugging import HuggingFaceInference
from helpers.spot import SpotifyClient
from helpers.vidgen import VideoGenerator
from helpers.tele import TeleGramClient
from helpers.youtube_download import YoutubeClientDownload
from helpers.youtube_upload import YoutubeClientUpload


class MainClass:
    def __init__(self, output_dir="generated_content") -> None:
        self.prompts = Prompts()
        self.hugging = HuggingFaceInference(self.prompts)
        # self.spoti = SpotifyClient()

        self.youtube_download = YoutubeClientDownload()
        self.youtube_upload = YoutubeClientUpload()
        self.video_gen = VideoGenerator()
        self.tele = TeleGramClient()
        self.output_dir = output_dir

    def convert_to_folder_name(self, folder_name, base_directory="."):
        folder_name = re.sub(r"[^\w\s]", "", folder_name)
        folder_name = re.sub(r"\s+", " ", folder_name)
        folder_name = folder_name.strip()
        folder_name = folder_name.replace(" ", "_").lower()
        if base_directory:
            folder_path = os.path.join(base_directory, folder_name)
            return folder_path
        return folder_name

    def create_folder(self, folder_name):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        return folder_name

    def run(self, chat_id, topic, song_name):
        if str(chat_id) == "123456789":
            print(f"Invalid Chat Id, so not repling to telegram")
            return
        print("Topic:", topic)

        current_dir = self.convert_to_folder_name(topic, self.output_dir)
        # delete existing folder
        if os.path.exists(current_dir):
            os.system(f"rm -rf {current_dir}")
        # create new folder
        self.create_folder(current_dir)

        image_generation_prompt = self.prompts.get_image_generation_prompt(topic)
        print("Generating prompts for image generation...")
        image_generation_response = self.hugging.get_json_response(image_generation_prompt)
        # image_generation_response = {
        #     "image_descriptions": [
        #         "The first image shows a group of Indian boys, dressed in bright yellow raincoats and sturdy rubber boots, eagerly splashing in the muddy puddles that have formed under the heavy downpour, their faces bright with unbridled joy.",
        #         "Next, the boys are seen building a makeshift mud castle, using their small, worn-out hands to mold the wet earth into elaborate towers and walls, their laughter echoing in the rain-soaked air.",
        #         "One boy, with mud-streaked cheeks, opens his eyes to find his carefully constructed mud sculpture has partially collapsed. With a determined look, he gets back to work, smoothing out the edges and reinforcing the structure.",
        #         "As the rain begins to subside, the boys gather around their mud creations, pointing out the details and carefully adding decorative elements like flowers and leaves, turning their simple mud art into elaborate pieces of nature's artwork.",
        #         "The final shot captures the boys as the clouds part, revealing a rainbow. The vibrant colors shine against the backdrop of their completed mud sculptures and the joyful smiles on their faces, marking the end of a perfect day of play and creation.",
        #     ],
        #     "introductory_text": "Boys revel in rain-soaked fun",
        #     "featured_song": "Baby Shark Dance (Pinkfong)",
        #     "spotify_search_query": "Rainy day playlist",
        # }
        
        image_descriptions = image_generation_response["image_descriptions"]
        introductory_text = image_generation_response["introductory_text"]
        featured_song = image_generation_response["featured_song"]
        audio_search_query = image_generation_response["spotify_search_query"]

        print("Introductory text:", introductory_text)
        print("Featured Song:", featured_song)
        print("Audio search query:", audio_search_query)
        print("Image Prompts:", image_descriptions)

        print("Downloading audio...")
        audio_path = self.convert_to_folder_name("audio", current_dir)
        self.create_folder(audio_path)

        audio_description = self.youtube_download.download_audio(song_name, audio_path)
        if audio_description is None:
            print("Failed to download audio. Trying with featured song...")
            audio_description = self.youtube_download.download_audio(
                featured_song, audio_path
            )
        if audio_description is None:
            print("Failed to download audio. Trying with audio search query...")
            audio_description = self.youtube_download.download_audio(
                audio_search_query, audio_path
            )

        if audio_description is None:
            print("Failed to download audio. So Exiting...")
            return
        # print(audio_description)
        print("Audio downloaded successfully!")
       

        print("Generating images...")
        images_path = self.convert_to_folder_name("images", current_dir)
        self.create_folder(images_path)

        image_seed = random.randint(0, 1000000)
        images_cnt = 0
        for idx, desc in enumerate(image_descriptions):
            try:
                file_name = os.path.join(images_path, f"image_{idx}.png")
                self.hugging.get_and_save_image(desc, file_name, image_seed)
            except Exception as e:
                print("Failed to generate image:", e)
                continue
            images_cnt += 1

        if images_cnt < 3:
            print("Failed to generate enough images for the video. Exiting...")
            return

        print("Images generated successfully!")
        
        print("Generating video...")
        video_path = self.convert_to_folder_name("video", current_dir)
        video_name = self.convert_to_folder_name(f"{topic} video", None) + ".mp4"
        self.create_folder(video_path)
        self.video_gen.generate_video(
            introductory_text, images_path, audio_path, video_path, video_name
        )
        print("Video generated successfully!")
        print(f"Video saved at: {os.path.join(video_path, video_name)}")

        print("Generating video meta...")
        video_meta_generation_prompt = self.prompts.get_video_meta_generation_prompt(
            "\n".join(image_descriptions)
        )
        video_meta_generation_response = self.hugging.get_json_response(
            video_meta_generation_prompt
        )
        title = video_meta_generation_response["title"]
        description = video_meta_generation_response["description"]
        tags = video_meta_generation_response["tags"]
        description = f"{description}\n\n{audio_description}"
        print("Title:", title)
        print("Description:", description)
        print("Tags:", tags)

        print("Uploading video to Telegram...")
        video_file_path = os.path.join(video_path, video_name)
       
        # self.tele.send_telegram_video(chat_id, video_file_path)
        print("Video uploaded successfully!")

        print("Sending video meta to Telegram...")
        message = f"Title: {title}\nDescription: {description}\nTags: {tags}"
        self.tele.send_telegram_message(chat_id, message)
        print("*** Process completed successfully! ***")

        # # TODO: code to get confirmation from user from telegram to upload to youtube

        print("Uploading video to YouTube...")
        video_file_path = os.path.join(video_path, video_name)
      
        self.youtube_upload.upload_video(video_file_path, title, description, tags, "human")
        print("Video uploaded successfully!")


if __name__ == "__main__":
    # Get the inputs from command line arguments
    # if len(sys.argv) != 4:
    # print("Usage: create_telegram_video.py <chat_id> <topic> <song>")
    # sys.exit(1)

    # chat_id = sys.argv[1]
    # topic = sys.argv[2]
    # song = sys.argv[3]
    # topics=["Panner Paratha full recipe","Allo parathe full receipe","Dal Makani full receipe" ,"Panner Butter Masala Full receipe" ,"Tradition Dance of India",
    #         "About national fruit of India" ,"Little Kids playing around"]
    topics = [
    "Dance Routine", 
    "Lip Sync Challenge", 
    "Before & After Transformation", 
    "Act Like Your Zodiac Sign", 
    "Movie Scene Reenactment", 
    "Friendship Humor", 
    "How I Start My Day", 
    "Funny Pet Reactions", 
    "A Day in My Life", 
    "Things Only [Your Profession] Understand", 
    "Food Review Challenge", 
    "ASMR Video", 
    "Fitness Transformation", 
    "How to Style [Clothing Item]", 
    "Motivational Quote in Action", 
    "Random Facts About Me", 
    "What's in My Bag", 
    "Vacation Throwback", 
    "My Favorite Hobby", 
    "Tips to Stay Productive", 
    "Pranking My Friends", 
    "Cooking Fails vs Wins", 
    "POV Comedy Skit", 
    "Dance Battle with Friends", 
    "Pet Glow-Up Challenge"
    ]
    songs = [
    "Flowers by Miley Cyrus", 
    "Bloody Mary by Lady Gaga", 
    "Unholy by Sam Smith & Kim Petras", 
    "Super Freaky Girl by Nicki Minaj", 
    "Movie dialogues from trending reels", 
    "What Was I Made For? by Billie Eilish", 
    "Stay by The Kid LAROI & Justin Bieber", 
    "Bad Habit by Steve Lacy", 
    "As It Was by Harry Styles", 
    "Kill Bill by SZA", 
    "Sunroof by Nicky Youre & dazy", 
    "Calm Down by Rema & Selena Gomez", 
    "Shivers by Ed Sheeran", 
    "Good 4 U by Olivia Rodrigo", 
    "Levitating by Dua Lipa", 
    "Happier Than Ever by Billie Eilish", 
    "Golden Hour by JVKE", 
    "Lovely by Billie Eilish & Khalid", 
    "Drivers License by Olivia Rodrigo", 
    "Die For You by The Weeknd", 
    "Industry Baby by Lil Nas X & Jack Harlow", 
    "Butter by BTS", 
    "Peaches by Justin Bieber", 
    "Watermelon Sugar by Harry Styles", 
    "Savage Love by Jason Derulo & Jawsh 685"
    ]
    for i in range(0,len(topics)):
        chat_id = "5041569211"
        topic =topics[i]
        song = songs[i]

        print(f"recieved chat_id: {chat_id}, topic:{topic}, song: {song}")

        main_obj = MainClass()
        main_obj.run(chat_id, topic, song)
    # print("***DONE***")
