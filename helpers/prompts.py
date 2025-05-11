import random


class Prompts:

    def __init__(self) -> None:
        self.human_topics = [
            "Laughing Babies",
            "Chubby Cheeked Toddlers",
            "Newborns Sleeping",
            "Toddlers Learning to Walk",
            "Kids Splashing in Puddles",
            "Children Blowing Bubbles",
            "Siblings Hugging",
            "Babies Making Funny Faces",
            "Toddlers Eating Messy Food",
            "Kids Playing with Pets",
            "Children Opening Presents",
            "Babies Holding Their Toes",
            "Children Playing Dress-Up",
            "Toddlers Dancing",
            "Kids Building Sandcastles",
            "Babies Taking Their First Steps",
            "Children Painting",
            "Families Laughing Together",
            "Kids on Swings",
            "Toddlers Playing in the Snow",
            "Babies in Halloween Costumes",
            "Children Playing in Leaves",
            "Toddlers Sharing Toys",
            "Babies Crawling",
            "Kids Feeding Ducks",
            "Toddlers Clapping",
            "Kids Playing Hide-and-Seek",
            "Babies with Funny Hairdos",
            "Kids Playing Musical Instruments",
            "Children Baking Cookies",
            "Babies Waving",
            "Siblings Playing Together",
            "Toddlers Climbing",
            "Kids Riding Bikes",
            "Babies Playing Peek-a-Boo",
            "Toddlers Trying to Talk",
            "Kids at the Beach",
            "Children Giving Flowers",
            "Babies Reaching for Things",
            "Toddlers and Bubbles",
            "Kids with Face Paint",
            "Babies Sleeping on Parents",
            "Children Holding Hands",
            "Toddlers Smiling with Missing Teeth",
            "Kids Reading Books",
            "Babies Touching Mirrors",
            "Children Playing with Balloons",
            "Toddlers Wearing Sunglasses",
            "Babies Playing with Food",
            "Children at the Playground",
            "Toddlers Holding Stuffed Animals",
        ]
        self.animal_topics = [
            "Sleeping Puppies",
            "Chubby Cheeked Toddlers",
            "Cuddly Kittens",
            "Baby Elephants Playing",
            "Golden Retriever Puppies",
            "Chubby Baby Animals",
            "Fluffy Ducklings Following Mom",
            "Toddlers with Puppies",
            "Baby Goats Jumping",
            "Hedgehogs Being Adorable",
            "Children Feeding Animals",
            "Chihuahua Puppies",
            "Siberian Husky Puppies",
            "Pandas Rolling Around",
            "Turtle Hatchlings",
            "Baby Deer (Fawns)",
            "Koalas Hugging Trees",
            "Baby Monkeys Playing",
            "Baby Penguins Walking",
            "Bunnies Hopping",
            "Baby Sloths Hanging",
            "Kittens Chasing Lasers",
            "Baby Horses (Foals)",
            "Cows with Calves",
            "Fluffy Chicks",
            "Otters Holding Hands",
            "Kids Splashing in Puddles",
            "Tiny Piglets",
            "Shiba Inu Puppies",
            "Parrots Mimicking Sounds",
            "Baby Dolphins Swimming",
            "Playful Baby Seals",
            "Penguins Sliding on Ice",
            "Cats Purring",
            "Baby Owls Learning to Fly",
            "Dogs Tilting Their Heads",
            "Fluffy Sheep in Fields",
            "Puppies with Big Paws",
            "Baby Bunnies Eating",
            "Puppies in Costumes",
            "Baby Koalas Sleeping",
            "Baby Pigs Playing",
            "Raccoon Kits Playing",
            "Labrador Puppies Chasing Balls",
            "Baby Alpacas",
            "Baby Donkeys",
            "Puppies Rolling Over",
            "Kangaroo Joeys",
            "Baby Hedgehogs Exploring",
        ]

    def get_image_generation_prompt(self, topic):
        image_generation_prompt = """
        Generate 5 vivid and detailed image descriptions that follow a thematic progression related to topic: {topic}. Each image should build upon the previous one to tell a story or depict a sequence of events. For example, if the topic is “A Day in Baby's Life,” the first image should describe waking up in the morning, and next image should describe baby taking shower.

        Additionally, create a short introductory text that will be shown with the first image. 

        For audio, provide two options:
        1. Featured song - A real, existing song (with title and artist) that fits the theme of the {topic}. This should be a joyful, upbeat, and well-known song that can be easily found on Spotify.
        2. Spotify search query - A more general search term to help find relevant pop music if the background song isn't available.

        Descriptions should provide clear, natural language and must contain topic: `{topic}` in it and capture the topic, progressing through the theme.
        Make sure to maintain consistency with the characters and their attire across all image descriptions.
        Note that the introductory text should be under 15 words and spotify search query must not exceed 5 words.

        Please return the response in the following JSON format:
        ```json
        {{
        "image_descriptions": ["<str>", "<str>", "<str>", "<str>", "<str>"],
        "introductory_text": "<str>",
        "featured_song": "<str>",
        "spotify_search_query": "<str>"
        }}
        ```
        """.strip()
        return image_generation_prompt.format(topic=topic)

    def get_video_meta_generation_prompt(self, image_prompts):
        video_meta_generation_prompt = """
        Using the following sentences, generate a YouTube video title, description, and relevant tags. The video will feature a sequence of images based on these sentences. The title should be catchy and engaging, the description should briefly summarize the video content, and the tags should help optimize the video for search.

        Sentences:
        {image_prompts}

        Please return the output in the following JSON format:
        ```json
        {{
        "title": "<str>",
        "description": "<str>",
        "tags": ["<str>", "<str>", "<str>", "<str>", "<str>"]
        }}
        ```
        """.strip()
        return video_meta_generation_prompt.format(image_prompts=image_prompts)

    def get_topic(self, category="human"):
        if category == "human":
            return random.choice(self.human_topics)
        elif category == "animal":
            return random.choice(self.animal_topics)
        else:
            return "Japanese Anime Characters"
