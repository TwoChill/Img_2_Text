import os
import requests
import pytesseract
import configparser

config = configparser.ConfigParser()
config.read("settings.config")

# Add your own Telegram Bot Token and ChatID to your own .config file.
log_bot_token = config['settings']['log_bot_token']
log_bot_id = config['settings']['log_bot_id']


def extract_text_from_image(image_path):
    extracted_text = pytesseract.image_to_string(image_path)
    return extracted_text


def send_text_to_telegram(chat_id, text):
    send_text = f'https://api.telegram.org/bot{log_bot_token}/sendMessage?chat_id={chat_id}&text={text}'
    requests.get(send_text)


def process_received_image(file_id, chat_id):
    file_info = requests.get(f'https://api.telegram.org/bot{log_bot_token}/getFile?file_id={file_id}').json()
    file_path = file_info['result']['file_path']

    image_url = f'https://api.telegram.org/file/bot{log_bot_token}/{file_path}'
    image_response = requests.get(image_url)

    image_filename = os.path.basename(file_path)
    with open(image_filename, 'wb') as img_file:
        img_file.write(image_response.content)

    extracted_text = extract_text_from_image(image_filename)

    send_text_to_telegram(chat_id, extracted_text)
    os.remove(image_filename)


def main():
    print("Listening for incoming messages...")
    bot_message = 'Ik ben klaar om je foto\'s te ontvangen!'
    send_text_to_telegram(log_bot_id, bot_message)
    offset = None

    while True:
        response = requests.get(f'https://api.telegram.org/bot{log_bot_token}/getUpdates?offset={offset}').json()
        for update in response['result']:
            if 'message' in update and 'photo' in update['message']:
                chat_id = update['message']['chat']['id']
                file_id = update['message']['photo'][-1]['file_id']
                process_received_image(file_id, chat_id)

            offset = update['update_id'] + 1


if __name__ == "__main__":
    main()
