from telethon import TelegramClient
import os
import json
from collections import Counter
import re
import io
import asyncio

# Define paths
path_booster_decr = r'./booster_decr.txt'
path_booster_inc = r'./booster_inc.txt'
path_negation = r'./negation.txt'
path_negative = r'./negative.txt'
path_positive = r'./positive.txt'
group_file_path = r'./group.txt'
output_file_path = r'/home/ubuntu/output.json'

# Function to load words from a file
def load_words(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        words = file.read().splitlines()
    return words

# Load the word lists
booster_decr = load_words(path_booster_decr)
booster_inc = load_words(path_booster_inc)
negation = load_words(path_negation)
negative = load_words(path_negative)
positive = load_words(path_positive)

# Function to calculate sentiment score
def calculate_sentiment_score(message, positive, negative, booster_inc, booster_decr, negation):
    # Initialize sentiment score
    score = 0

    # Tokenize the message
    words = tokenize(message)

    # Iterate through the words and calculate the sentiment score
    for word in words:
        if word in positive:
            score += 1
        elif word in negative:
            score -= 1
        elif word in booster_inc:
            score *= 2
        elif word in booster_decr:
            score /= 2
        elif word in negation:
            score = -score

    return score

# Function to clean and tokenize text
def tokenize(text):
    # Remove special characters and convert to lowercase
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text).lower()

    # Split the text into words
    words = text.split()

    return words

async def main():
    # Create and connect the client
    api_id = ''
    api_hash = ''
    phone = ''
    client = TelegramClient('session_name', api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        await client.sign_in(phone, input('Enter the code: '))

    print("Client connected and authorized.")

    # Retrieve group name from file
    with open(group_file_path, 'r', encoding='utf-8') as file:
        group_name = file.read().strip()

    # Collect messages from the specified group
    messages = await client.get_messages(group_name, limit=200)
    print(f"Retrieved {len(messages)} messages.")

    # Initialize statistics
    total_messages = 0
    word_counter = Counter()
    sentiment_scores = []

    # Check if output directory exists, create if not
    output_dir = os.path.dirname(output_file_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Analyze messages and store the results
    message_data = []
    for message in messages:
        if message.text:
            total_messages += 1
            words = tokenize(message.text)
            word_counter.update(words)
            sentiment_score = calculate_sentiment_score(message.text, positive, negative, booster_inc, booster_decr, negation)
            sentiment_scores.append(sentiment_score)
            message_data.append({
                'text': message.text,
                'sentiment_score': sentiment_score
            })

    print(f"Processed {total_messages} messages.")

    # Calculate average sentiment score
    average_sentiment_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0

    # Prepare the output data
    output_data = {
        'group_name': group_name,
        'total_messages': total_messages,
        'word_frequency': dict(word_counter.most_common()),
        'average_sentiment_score': average_sentiment_score,
        'messages': message_data
    }

    # Write the output data to a JSON file
    with io.open(output_file_path, 'w', encoding='utf-8') as output_file:
        json.dump(output_data, output_file, ensure_ascii=False, indent=4)

    print("Output written to file.")

    # Disconnect the client
    await client.disconnect()
    print("Client disconnected.")

if __name__ == '__main__':
    asyncio.run(main())
