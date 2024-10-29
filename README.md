# README.md

## Fall 2024 Project 1

### Author
Manoj Virinchi Chitta

### Overview
This project provides a redaction system that censors sensitive information (names, dates, phone numbers, addresses, emails, and concepts) from plain text files. Using the `spaCy` library for natural language processing and `nltk` for synonym extraction, this system allows flexible, rule-based, and context-based redaction of sensitive information. 
The program redacts data by replacing detected sensitive information with a series of "█" characters, preserving the length of the original content. 

### Installation
1. Ensure Python 3.12 . Create the pipfile and pipfile.lock and then create virtual environment
    ```bash
   pipenv install 
   pipenv shell
   ```

2. Install the required libraries (`spaCy` and `nltk`) are installed.
    ```bash
   pipenv install spacy nltk
   ```
3. Install the `en_core_web_lg` model for spaCy by running:
   ```bash
   python -m spacy download en_core_web_lg
   ```
4. The code downloads `nltk's wordnet` while executing . But if you wanna execute it manually you can follow the below command:
   ```bash
   python -m nltk.downloader wordnet
   ```
 

### How to Run
To execute the program, use the command:
```bash
python redactor.py --input "data/*.txt" --names --dates --phones --address --emails --concept "concept1"  --output "output_dir" --stats "stdout/example.txt"
```
This command redacts all the specified categories and writes the results to the files directory with `_censored` being appended to the filename of the input file, with statistics printed to stdout or in an output file.

### Redaction Process and Methods

Each sensitive data type is redacted through a dedicated method within the `Redactor` class. The program ensures the preservation of spaces between names and other elements, so readability is only affected within redacted content itself.

#### `redact_names`
- **Description**: Detects names using spaCy's `PERSON` entity and a regex for names in all caps with initials or suffixes. Redacts each name while preserving spaces and special characters within the name.
- **Example**: `"JOHN DOE"` is redacted as `"████████"`, preserving the space between the first and last name.

#### `redact_dates`
- **Description**: Detects dates using spaCy's `DATE` entity and various regex patterns for date formats. Known formats like `MM/DD/YYYY`, `Month Day Year`, and weekdays are handled.
- **Example**: `"June 18, 2024"` becomes `"███████, ████"`.

#### `redact_phones`
- **Description**: Identifies phone numbers with a regex pattern that captures formats such as `(123) 456-7890` or `123-456-7890`. All matched phone numbers are redacted while maintaining punctuation.
- **Example**: `"(123) 456-7890"` becomes `"██████████████"`.

#### `redact_address`
- **Description**: Matches common address formats (e.g., street names with suffixes like `Ave`, `Blvd`, etc.). It also uses spaCy's entities `GPE`, `LOC`, and `FAC` to detect geographic locations or facilities. Spaces within addresses are preserved.
- **Example**: `"Main ST"` becomes `"███████"`.

#### `redact_emails`
- **Description**: Detects emails with a regex and redacts them entirely while maintaining readability by replacing each character with a `█`.
- **Example**: `"user@example.com"` becomes `"███████████████"`.

#### `redact_concept`
- **Description**: Uses NLP to identify sentences containing specified concepts, and then redacts the entire sentence. Each concept's synonyms (using `nltk.wordnet`) are also used to broaden the redaction scope. This method is sensitive to plural forms and similar words for broader coverage.
- **Example**: Given the concept `"wine"`, sentences with "wine" or synonyms like "beverage" or pluralized forms ("wines") are redacted.
- **Special Handling**: Sentences containing both specified concepts and certain context-specific words like "these" are also redacted to ensure comprehensive contextual redaction.

#### `redact_preserving_special_chars`
- **Description**: Maintains special characters while redacting sensitive content within names, dates, or addresses. Characters such as commas, periods, and dashes are preserved.

### Test Case Files

The project includes test files to validate each redaction method. These tests ensure accurate detection and redaction of sensitive data, including edge cases. Below are descriptions of each test file:

- **`test_redact_address.py`**: Ensures the `redact_address` function accurately detects and redacts various address formats.
- **`test_redact_concepts.py`**: Ensures `redact_concept` accurately redacts sentences containing specified concepts and their synonyms.
- **`test_redact_dates.py`**: Tests that the `redact_dates` function captures various date formats and performs redaction appropriately.This will also ensure the days are being redacted. 
- **`test_redact_emails.py`**: Confirms that email patterns are detected and redacted without affecting surrounding content.
- **`test_redact_names.py`**: Checks the `redact_names` function’s ability to recognize and redact person names, especially in cases involving initials or all-uppercase formats.
- **`test_redact_phones.py`**: Validates the `redact_phones` function against multiple phone number formats, ensuring consistent redaction.
- **`test_redact_whitelisting.py`**: Ensures that specified terms (like email headers) are excluded from redaction by verifying functionality of the whitelisting feature.

### Assumptions and Known Bugs

- **Assumptions**:
  - Synonyms retrieved for concepts are comprehensive enough to cover various sentence structures where sensitive terms may appear.
  - Common address formats and abbreviations are assumed to be sufficient for identifying address information.
  - Whitelisted terms are case-sensitive and only matched exactly as defined.
  - The program also assumes that spaCy’s GPE, LOC, and FAC entities cover all location-related information that might need redaction. I have also provided extra Street names and address formats to capture various address formats.
  - The code uses case-insensitive matching for names, dates, and concepts. This assumes that sensitive information could appear in any case, so it attempts to capture all variations without distinguishing between uppercase and lowercase letters.
  

- **Known Bugs**:
  - Synonyms detection may not catch uncommon or highly contextual synonyms.
  - Redaction using spaCy entities can sometimes result in false positives if a term closely matches the entity type (e.g., "Washington" as both a name and location).
  - When we use ORG as the entity for detecting various organisation names , it is also detecting various non-organisation names as names and redacting it. So I have not considered the ORG entity
  - If the address is starting with number like `3800 Main St` it is not redacting the number as the spacy model is not recognising that as a address.


