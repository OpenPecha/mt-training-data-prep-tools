import json

import requests


def translate_input_sentence(input_sentence, language):
    # Prepare the payload data
    payload = {
        "input_sentence": input_sentence,
        "level_of_explanation": 0,
        "language": language,
        "model": "NO",
    }

    # Convert the payload to JSON
    json_payload = json.dumps(payload)

    # Set the headers
    headers = {"Content-Type": "application/json"}

    # Make the POST request
    response = requests.post(
        "https://dharmamitra.org/api/translation/", headers=headers, data=json_payload
    )

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Return the translation
        return response.text
    else:
        print("Translation error:", response.status_code)
        return None


# REPL loop
while True:
    # Ask for the input sentence from the user
    print("Enter the input sentence (press Enter twice to finish):")
    lines = []
    while True:
        line = input()
        if line:
            lines.append(line)
        else:
            break

    # Join the lines into a single string
    input_sentence = "\n".join(lines)

    # Ask for the language from the user
    language = input("Enter the language (e.g., bo-en), or 'exit' to quit: ")

    if language.lower() == "exit":
        # Exit the REPL loop if the user chooses to exit
        break

    # Perform translation
    translation = translate_input_sentence(input_sentence, language)

    if translation is not None:
        # Print the translation
        print("Translation:")
        print(translation)
        print("------------------------------------------------")
