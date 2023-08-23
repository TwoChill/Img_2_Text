import os
import requests
import pytesseract
import configparser
from io import BytesIO
from PIL import Image

# Read configuration from the settings file
config = configparser.ConfigParser()
config.read("settings.config")
log_bot_token = config['settings']['log_bot_token']
log_bot_id = config['settings']['log_bot_id']

# # Delete the received image message from the chat if True
delete_img = False


# Extract text from image data using OCR
def extract_text_from_image(image_data):
    image = Image.open(BytesIO(image_data))
    extracted_text = pytesseract.image_to_string(image)
    return extracted_text


# Send text message to a chat using the Telegram API
def send_text_to_telegram(chat_id, text):
    send_text = f'https://api.telegram.org/bot{log_bot_token}/sendMessage?chat_id={chat_id}&text={text}'
    requests.get(send_text)


# Process received image and send extracted text back
def process_received_image(image_data, chat_id, message_id):
    extracted_text = extract_text_from_image(image_data)
    send_text_to_telegram(chat_id, extracted_text)

    if delete_img is True:
        # Delete the received image message from the chat
        delete_message_url = f'https://api.telegram.org/bot{log_bot_token}/deleteMessage?chat_id={chat_id}&message_id={message_id}'
        requests.get(delete_message_url)


# Main function to listen for incoming messages and process images
def main():
    print("Listening for incoming messages...")
    bot_message = "I'm ready to convert your photos!"
    send_text_to_telegram(log_bot_id, bot_message)
    offset = None

    while True:
        response = requests.get(f'https://api.telegram.org/bot{log_bot_token}/getUpdates?offset={offset}').json()
        for update in response['result']:
            if 'message' in update and 'photo' in update['message']:
                chat_id = update['message']['chat']['id']
                message_id = update['message']['message_id']  # Get the message ID
                file_id = update['message']['photo'][-1]['file_id']

                # Fetch the file data directly using getFile and download it
                file_info = requests.get(
                    f'https://api.telegram.org/bot{log_bot_token}/getFile?file_id={file_id}').json()
                file_path = file_info['result']['file_path']
                file_url = f'https://api.telegram.org/file/bot{log_bot_token}/{file_path}'
                image_response = requests.get(file_url).content

                process_received_image(image_response, chat_id, message_id)  # Pass the message ID

            offset = update['update_id'] + 1


if __name__ == "__main__":
    main()
