import os
from glob import glob
from openai import OpenAI
import time
from dotenv import load_dotenv


load_dotenv()

MODEL = "gpt-4.1-mini"

SYSTEM_PROMPT = """
You are an expert text cleaning assistant. Your task is to take raw, messy text extracted from a PDF and do the following:
1.  Correct any OCR errors, typos, or formatting issues.
2.  Remove all non-English text.
3.  Ensure the final output is clean, readable, and perfectly formatted English text.
4.  Do not add any commentary, greetings, or apologies. Only output the cleaned text.
"""
TEXT_FOLDER = "irdai_pdfs/texts"


def clean_with_gpt(client, text_content):
    """Uses GPT-4 to clean the provided text."""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text_content},
            ],
            temperature=0.1,  # Low temperature for more deterministic output
            max_tokens=4096,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"  - Error calling OpenAI API: {e}")
        # Return original text on failure
        return text_content


def main():
    """Loops through text files, cleans them with GPT, and overwrites them."""

    # Check for API key
    if "OPENAI_API_KEY" not in os.environ:
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set your OpenAI API key and re-run the script.")
        return

    client = OpenAI()

    text_files = glob(os.path.join(TEXT_FOLDER, "*.txt"))
    print(f"Found {len(text_files)} text files to clean.")

    for file_path in text_files:
        print(f"Cleaning {file_path}...")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read()

            # Skip if file is empty
            if not raw_text.strip():
                print("  - Skipping empty file.")
                continue

            cleaned_text = clean_with_gpt(client, raw_text)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(cleaned_text)

            print(f"  - Successfully cleaned and saved.")

            # Add a delay to avoid hitting API rate limits
            time.sleep(1)

        except Exception as e:
            print(f"  - An error occurred: {e}")

    print("\nDone cleaning all text files.")


if __name__ == "__main__":
    main()
