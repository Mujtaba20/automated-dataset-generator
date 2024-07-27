import ast
import google.generativeai as genai
import os
import json
import ast
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("API_KEY"))


def translate(old_dataset, new_dataset, num_sentences):
    """
    Reads a specified number of English sentences from the old_dataset and appends them to the new_dataset.

    Parameters:
        old_dataset (str): The path to the file containing the old dataset.
        new_dataset (str): The path to the file where the new dataset will be appended.
        num_sentences (int): The number of English sentences to read from the old dataset.

    Returns:
        None
    """

    sentences = []

    # Read English sentences from the old dataset
    with open(old_dataset, 'r', encoding='utf-8') as old_file:
        for line in old_file:
            parts = line.strip().split('\t')
            if len(parts) >= 3:  # Ensure there are at least three parts (English, German, Hindi)
                english_sentence = parts[0].strip()
                sentences.append(english_sentence)
            if len(sentences) >= num_sentences:
                break
    print(sentences)
    # Using `response_mime_type` requires one of the Gemini 1.5 Pro or 1.5 Flash models
    model = genai.GenerativeModel('gemini-1.5-flash',
                                  # Set the `response_mime_type` to output JSON
                                  generation_config={"response_mime_type": "application/json"})

    prompt = (
      f"translate All These these English sentences: {sentences}. here if you get any sentence repeatation then try to find the duplicate sentence's different meaning or translation in the hindi and german language. plz do english sentence language translation in hindi or german language if the english sentence is repeated multiple times then translate it in different meaning. do not mention that the specific sentence has different meaning.\n",
      "Using this JSON schema:\n",
      '  Translation = {"German": "German tranlation sentence","Hindi":"Hindi tranlation sentence"}\n',
      'Return {"English sentence",Translation}',
    )

    response = model.generate_content(prompt).text
    print(response)
    dictsentences = ast.literal_eval(response)
    print("::::::::::::::::")
    print(dictsentences)

# Example usage
old_dataset = "dataset.txt"
new_dataset = "new_data.txt"
translate(old_dataset, new_dataset, 10)  # Append 5 English sentences from dataset.txt to new_data.txt
