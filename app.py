import openai
from dotenv import load_dotenv
import os
import ast
import subprocess
import time

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(
    api_key=api_key,
)
system = "You are a Translater who can translate english sentences into german and hindi and return sentences in json like {engSentence:{'german':'sentence', 'hindi':'sentence'}}."
message = []
message.append({"role": "system", "content": system})


def add_sentences_to_dataset(dataset_path, sentences):
    with open(dataset_path, 'a', encoding='utf-8') as file:
        for eng_sentence, translations in sentences.items():
            german_sentence = translations.get('german', '')
            hindi_sentence = translations.get('hindi', '')
            file.write(f"{eng_sentence}\t{german_sentence}\t{hindi_sentence}\n")


def remove_lines_from_dataset(dataset_path, sentences_to_remove):
    with open(dataset_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open(dataset_path, 'w', encoding='utf-8') as file:
        for line in lines:
            english_sentence = line.strip().split('\t')[0]
            if english_sentence not in sentences_to_remove:
                file.write(line)


def translate(old_dataset, new_dataset, num_sentences):
    sentences = []

    with open(old_dataset, 'r', encoding='utf-8') as old_file:
        for line in old_file:
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                english_sentence = parts[0].strip()
                sentences.append(english_sentence)
            if len(sentences) >= num_sentences:
                break

    new_message = {"role": "user", "content": f"translate all these sentence: {sentences}. here if you get any sentence repeatation then try to find the duplicate sentence's different meaning or translation in the hindi and german language. plz do english sentence language translation in hindi or german language if the english sentence is repeated multiple times then translate it in different meaning. do not mention that the specific sentence has different meaning."}
    message.append(new_message)
    response = client.chat.completions.create(
      model="gpt-3.5-turbo-0125",
      messages=message,
      response_format={"type": "json_object"},
    )

    translator = response.choices[0].message.content
    print(translator)
    dictsentences = ast.literal_eval(translator)
    add_sentences_to_dataset(new_dataset, dictsentences)
    remove_lines_from_dataset(old_dataset, sentences)


def commit_and_push_changes(repo_path, files_to_commit, commit_message):
    subprocess.run(["git", "-C", repo_path, "add"] + files_to_commit, check=True)
    subprocess.run(["git", "-C", repo_path, "commit", "-m", commit_message], check=True)
    subprocess.run(["git", "-C", repo_path, "push"], check=True)


def main(old_dataset, new_dataset, repo_path):
    while os.path.getsize(old_dataset) > 0:
        translate(old_dataset, new_dataset, 10)
        commit_and_push_changes(repo_path, [old_dataset, new_dataset], "Update datasets")
        time.sleep(5)

    # Initial commit if repository is empty
    if not os.listdir(repo_path):
        subprocess.run(["git", "-C", repo_path, "commit", "--allow-empty", "-m", "Initial commit"], check=True)
        subprocess.run(["git", "-C", repo_path, "push"], check=True)


# Example usage
old_dataset = "dataset.txt"
new_dataset = "new_data.txt"
repo_path = "/home/ubuntu/automated-dataset-generator"  # Local path of your cloned repository
main(old_dataset, new_dataset, repo_path)
