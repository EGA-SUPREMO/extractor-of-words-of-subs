import sqlite3
import os
import platform
import re # Import the regular expression module

def find_anki_database():
    """
    Attempts to find the Anki database file (collection.anki2 or .anki21).
    Returns the path to the database file or None if not found.
    """
    base_paths = []
    if platform.system() == "Windows":
        app_data = os.getenv('APPDATA')
        if app_data:
            base_paths.append(os.path.join(app_data, 'Anki2'))
    elif platform.system() == "Darwin": # macOS
        base_paths.append(os.path.expanduser('~/Library/Application Support/Anki2'))
    else: # Linux and others
        # Standard Linux paths
        base_paths.append(os.path.expanduser('~/.local/share/Anki2'))
        base_paths.append(os.path.expanduser('~/Anki')) # Older versions or custom
        base_paths.append(os.path.expanduser('~/.anki')) # Even older versions
        # Flatpak specific path
        base_paths.append(os.path.expanduser('~/.var/app/net.ankiweb.Anki/data/Anki2'))


    for base_path in base_paths:
        if os.path.exists(base_path):
            # Look for profiles (each profile has a separate database)
            # In Flatpak, the "Anki2" folder is directly under data/, not in a profile subfolder
            # but we keep the loop structure to be compatible with standard installs

            # For standard installs, list items are profiles
            # For Flatpak, the base_path *is* the Anki2 directory
            items_to_check = os.listdir(base_path) if any(p in base_path for p in ['Anki2', '.anki']) else ['.'] # Check '.' for the flatpak case where base_path is already Anki2


            for item in items_to_check:
                profile_path = os.path.join(base_path, item)
                # Ensure it's a directory or the base_path itself in the flatpak case
                if os.path.isdir(profile_path) or (item == '.' and os.path.exists(profile_path)):
                    # Check for both .anki21 and .anki2 extensions
                    db_path_21 = os.path.join(profile_path, 'collection.anki21')
                    if os.path.exists(db_path_21):
                        return db_path_21
                    db_path_2 = os.path.join(profile_path, 'collection.anki2')
                    if os.path.exists(db_path_2):
                        return db_path_2


    return None


def clean_field_text(text):
    """
    Removes HTML tags and content within square brackets (like sound tags).
    """
    # Remove HTML tags
    cleaned_text = text.replace('<br>', '\n').replace('<div>', '\n').replace('</div>', '').strip()
    # Remove content within square brackets (e.g., [sound:...])
    cleaned_text = re.sub(r'\[.*?\]', '', cleaned_text)
    return cleaned_text


def extract_front_fields(db_path):
    """
    Connects to the Anki database and extracts and cleans the front field from each note.
    Args:
        db_path (str): The path to the Anki database file.
    Returns:
        list: A list of strings, where each string is the cleaned text from the front
              of a card.
    """
    front_fields = []
    conn = None # Initialize conn to None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT flds FROM notes")

        for row in cursor.fetchall():
            fields = row[0].split('\x1f')
            if fields:
                # Get the raw front field text
                raw_front_text = fields[0]
                # Clean the text
                cleaned_front_text = clean_field_text(raw_front_text)
                front_fields.append(cleaned_front_text)

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

    return front_fields



def compare(anki_words):
    word_file_path = "sub.txt"

    words_not_in_anki = [] # List to store words from the file not found in Anki

    try:
        with open(word_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                word_from_file = line.strip()
                if not word_from_file:
                    continue

                if word_from_file.lower() not in anki_words:
                    words_not_in_anki.append(word_from_file)
    except FileNotFoundError:
        print(f"\nError: The file '{word_file_path}' was not found.")
        words_not_in_anki = None

    return words_not_in_anki

def output_words(words_not_in_anki):
    if words_not_in_anki is not None: # Check if file reading was successful
        if words_not_in_anki:
            print("\n--- Words from the file NOT found in Anki front fields ---")
            # Use a set and sort for a clean, unique output list
            unique_words_not_found = sorted(list(set(words_not_in_anki)))
            for word in unique_words_not_found:
                print(word)
            print(f"\nTotal unique words from file not found in Anki: {len(unique_words_not_found)}")
        else:
            print("\nAll words from the file were found in Anki front fields.")



if __name__ == "__main__":
    db_path = find_anki_database()

    if db_path:
        print(f"Found Anki database at: {db_path}")
        front_texts = extract_front_fields(db_path)

        if front_texts:
            all_words = []
            for text in front_texts:
                words_in_current_text = text.split()

                all_words.extend(words_in_current_text)
            

            print(f"Extracted {len(all_words)} words in total.")
            all_words_lower_set = set(word.lower() for word in all_words)

            words_not_in_anki = compare(all_words_lower_set)
            output_words(words_not_in_anki)

        else:
            print("No front fields extracted. The database might be empty or structured differently.")
    else:
        print("Anki database not found.")