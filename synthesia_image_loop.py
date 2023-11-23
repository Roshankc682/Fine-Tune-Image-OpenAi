# Import necessary libraries
import openai  # Add this line
import requests
import base64
import time


# Set your OpenAI API key
api_key = ""
openai.api_key = api_key

# Function for the Vision API description call
def vision_api_describe_image(image_base64):
    response =openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        # model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64, {image_base64}"
                        }
                    },
                    {
                        "type": "text",
                        # "text": "Describe the image in detail (colors, features, theme, style, etc)"
                    }
                ]
            },
        ],
        max_tokens=500
    )

    # Accessing the content correctly
    description_text = response.choices[0].message['content']

    return description_text

# Function for generating an image with DALL-E API
def dalle_api_generate_image(description):
    response = openai.Image.create(
        model="dall-e-3",
        prompt=description,
        n=1
    )

    return response.data[0].url

    # return response.assets[0].url

# Function for the Vision API comparison and improved description call
def vision_api_compare_and_describe(reference_image_base64, synthetic_image_base64):
    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64, {reference_image_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "Describe both images in detail (colors, features, theme, style, etc), then compare them. Finally create a new and improved description prompt to match the reference image as close as possible."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64, {synthetic_image_base64}"
                        }
                    }
                ]
            }
        ],
        max_tokens=300
    )

    # Accessing the content correctly
    improved_description_text = response.choices[0].message['content']

    return improved_description_text


import random
import string

def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))


# Function to encode an image to base64 (define or replace with your implementation)
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
    return image_base64

# Iterative image synthesis function
def iterative_image_synthesis(reference_image_path, iterations=3):

    descriptions = []
    synthetic_images_urls = []

    reference_image_base64 = encode_image_to_base64(reference_image_path)
    synthetic_image_base64 = ""  # Initialize appropriately
    

    for i in range(iterations):
        if i == 0:
            # Initial description from the reference image
            description = vision_api_describe_image(reference_image_base64)
        else:
            # Get an improved description by comparing the reference and the latest synthetic image
            description = vision_api_compare_and_describe(reference_image_base64, synthetic_image_base64)

        descriptions.append(description)

        # Fine-tune the description (for simplicity, we add "high detail")
        fine_tuned_description = f"{description} in high detail"
        synthetic_image_url = dalle_api_generate_image(fine_tuned_description)
        synthetic_images_urls.append(synthetic_image_url)

        # Fetch the synthetic image from the URL
        synthetic_image_response = requests.get(synthetic_image_url)

        if synthetic_image_response.status_code == 200:
            synthetic_image_content = synthetic_image_response.content
            synthetic_image_base64 = base64.b64encode(synthetic_image_content).decode('utf-8')

            # Save the synthetic image content to a file
            random_strings = generate_random_string(10)
            synthetic_image_path = f'/Users/roshan/Desktop/img_generation/{random_strings}{i}.png'
            with open(synthetic_image_path, 'wb') as image_file:
                image_file.write(synthetic_image_content)
                print(f"Synthetic image saved at: {synthetic_image_path}")
        else:
            print(f"Failed to fetch synthetic image for iteration {i+1}: Status code {synthetic_image_response.status_code}")
            # Skip the iteration if the image couldn't be fetched
            continue

        # Automated Quality Check (simple version)
        # Here we are using the Length of the description as a proxy for detail
        # A more sophisticated approach would be needed for a real application
        current_description_length = len(description)

        if i > 0 and current_description_length <= len(descriptions[-2]):
            print(f"No significant improvement in detail detected in iteration {i+1}.")
            # Optionally, we could decide to stop iterating if there's no improvement

        print(f"Iteration {i+1}: Description: {fine_tuned_description}")
        time.sleep(5)  # Sleep to avoid hitting API rate limits

    return descriptions, synthetic_images_urls

# Absolute path to your reference image
reference_image_path = '/Users/roshanMac//Desktop/img_generation/Designer_3.png'

# Call the iterative synthesis function with the path to your reference image
iterative_image_synthesis(reference_image_path)
