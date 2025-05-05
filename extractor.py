import webvtt # For parsing VTT files
import string # For punctuation removal
import sys     # For file operations (like cleanup)

# --- Function to Extract Text from VTT ---
def extract_text_from_vtt(vtt_filepath):
  """
  Reads a VTT file and extracts all caption text into a single string.

  Args:
    vtt_filepath (str): The path to the VTT file.

  Returns:
    str: A single string containing all concatenated caption text,
         or None if an error occurs.
  """
  all_text = ""
  try:
    vtt = webvtt.read(vtt_filepath)
    for caption in vtt:
      # Add the caption text, followed by a space to separate words
      # between captions potentially
      all_text += caption.text + " "
    # Strip leading/trailing whitespace that might accumulate
    return all_text.strip()
  except FileNotFoundError:
    print(f"Error: VTT file not found at '{vtt_filepath}'")
    return None
  except webvtt.errors.MalformedFileError:
    print(f"Error: The file '{vtt_filepath}' is not a valid VTT file or is malformed.")
    return None
  except Exception as e:
    print(f"An unexpected error occurred while reading the VTT file: {e}")
    return None

# --- Function to Extract Unique Words from Text ---
def extract_unique_words_from_text(text):
  """
  Takes a string of text, extracts all unique words, and returns them as a list.

  Args:
    text (str): The input text string.

  Returns:
    list: A list of unique words found in the text, sorted alphabetically.
          Returns an empty list if the input text is empty or None.
  """
  if not text:
      return []

  try:
      # 1. Convert to lowercase
      text = text.lower()

      # 2. Remove punctuation
      translator = str.maketrans('', '', string.punctuation)
      text = text.translate(translator)

      # 3. Split into words
      words = text.split()

      # 4. Find unique words using a set
      unique_word_set = set(words)

      # 5. Convert set back to a list and sort it
      unique_word_list = sorted(list(unique_word_set))

      return unique_word_list
  except Exception as e:
      print(f"An error occurred during unique word extraction: {e}")
      return []

# --- Function to Save Words to File ---
def save_words_to_file(word_list, output_filepath):
  """
  Saves a list of words to a specified file, each word on a new line.

  Args:
    word_list (list): The list of words to save.
    output_filepath (str): The path to the output file.

  Returns:
    bool: True if saving was successful, False otherwise.
  """
  try:
    with open(output_filepath, 'w', encoding='utf-8') as outfile:
      for word in word_list:
        outfile.write(word + '\n') # Write each word followed by a newline
    print(f"Successfully saved unique words to '{output_filepath}'")
    return True
  except Exception as e:
    print(f"An error occurred while saving the file: {e}")
    return False

# --- Main Execution ---
if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("Usage: python3 extract.py <input_vtt_file>")
        sys.exit(1) # Exit the script indicating an error

    input_vtt_file = sys.argv[1] # Get the first argument as the input file

    output_unique_words_file = input_vtt_file + ' - nodup.txt'


    # --- Processing Steps ---
    print(f"\nProcessing VTT file: '{input_vtt_file}'...")
    # 1. Extract text from VTT
    extracted_text = extract_text_from_vtt(input_vtt_file)

    if extracted_text is not None:
        print("VTT text extracted successfully.")
        # print("\n--- Extracted Text ---")
        # print(extracted_text) # Optional: print the full extracted text
        # print("----------------------")

        # 2. Extract unique words from the text
        print("\nExtracting unique words...")
        unique_words = extract_unique_words_from_text(extracted_text)

        if unique_words:
            print(f"Found {len(unique_words)} unique words.")
            # print("\n--- Unique Words ---")
            # for word in unique_words: # Optional: print unique words here
            #     print(f"- {word}")
            # print("--------------------")

            # 3. Save the unique words to the output file
            print(f"\nAttempting to save unique words to '{output_unique_words_file}'...")
            save_words_to_file(unique_words, output_unique_words_file)
        else:
            print("No unique words found in the extracted text.")
    else:
        print("Could not extract text from VTT file. Aborting.")

    # --- Optional: Clean up the dummy files ---
    #try:
        #if os.path.exists(input_vtt_file):
            #os.remove(input_vtt_file)
            #print(f"\nRemoved sample VTT file: '{input_vtt_file}'")
        #if os.path.exists(output_unique_words_file):
            # Keeping the output file might be desired, but we remove it for cleanup
            #os.remove(output_unique_words_file)
            #print(f"Removed output file: '{output_unique_words_file}'")
    #except OSError as e:
    #    print(f"Error removing sample files: {e}")

