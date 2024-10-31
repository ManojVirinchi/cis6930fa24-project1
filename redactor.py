import argparse
import glob
import os
import spacy
from spacy.matcher import PhraseMatcher
import re
import nltk
from nltk.corpus import wordnet
from spacy.tokens import Token
import numpy as np

class Redactor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
        self.matcher = PhraseMatcher(self.nlp.vocab,attr ="LOWER")
        self.stats = {
            "names": 0,
            "dates": 0,
            "phones": 0,
            "addresses": 0,
            "emails" :0,
            "concepts": {}
        }
        # nltk.download('punkt')
        nltk.download('wordnet')
        # nltk.download('omw-1.4')
        self.whitelist = {"Content-Type", "Content-Transfer-Encoding","X-Origin","Mime-Version"}

    def is_whitelisted(self, term):
        return term in self.whitelist
    
    def redact_emails(self, text):
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        matches = re.findall(email_pattern, text)
        for match in matches:
            text = text.replace(match, "█" * len(match))
            self.stats["emails"] += 1
        return text

    def redact_names(self, text):
        lines = text.split('\n')
        redacted_lines = []
        for line in lines:
            doc = self.nlp(line)
            redacted_line = line
            
            all_caps_name_pattern = re.compile(r'\b[A-Z]+(?:\s+[A-Z]\.?)+(?:\s+[A-Z]+\.?)*\b')
            
            for match in all_caps_name_pattern.finditer(redacted_line):
                if not self.is_whitelisted(match.group()):
                    redacted = self.redact_preserving_special_chars(match.group())
                    redacted_line = redacted_line.replace(match.group(), redacted)
                    self.stats["names"] += 1
            
            for ent in doc.ents:
                if ent.label_ in ["PERSON"] and not self.is_whitelisted(ent.text):
                    redacted = self.redact_preserving_special_chars(ent.text)
                    redacted_line = redacted_line.replace(ent.text, redacted)
                    self.stats["names"] += 1
            
            redacted_lines.append(redacted_line)
        return '\n'.join(redacted_lines)

    def redact_preserving_special_chars(self, text):
        special_chars = '<>,.;:()[]{}/'
        redacted = ''
        for char in text:
            if char in special_chars:
                redacted += char
            else:
                redacted += '█'
        return redacted

    def redact_dates(self, text):
        doc = self.nlp(text)
        redacted_text = text
        for ent in doc.ents:
            if ent.label_ == "DATE" and not self.is_whitelisted(ent.text):
                redacted_text = redacted_text.replace(ent.text, "█" * len(ent.text))
                self.stats["dates"] += 1

        # Additional regex patterns for dates
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  
            r'\b\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{2,4}\b',  
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s\d{1,2}(?:\s\d{2,4})?\b'
            r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2}\b',  
            r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b'  
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, redacted_text)
            for match in matches:
                if not self.is_whitelisted(match):
                    redacted_text = redacted_text.replace(match, "█" * len(match))
                    self.stats["dates"] += 1

        return redacted_text

    def redact_phones(self, text):
        phone_pattern = re.compile(r'\b(?:\d{3}[-.\s]??\d{3}[-.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-.\s]??\d{4}|\d{3}[-.\s]??\d{4})\b')
        matches = phone_pattern.findall(text)
        for match in matches:
            if not self.is_whitelisted(match):
                text = text.replace(match, "█" * len(match))
                self.stats["phones"] += 1
        return text

    def redact_address(self, text):
        doc = self.nlp(text)
        redacted_text = text

        
        street_suffixes = r'(?:St|Street|Ave|Avenue|Blvd|Boulevard|Rd|Road|Ln|Lane|Dr|Drive|Ct|Court|Pl|Place|Ter|Terrace|Way|Cir|Circle|Pkwy|Parkway)'
        
        address_patterns = [
            rf'\b\d+\s+(?:[A-Za-z0-9\s-]+(?:{street_suffixes})\.?)(?:\s+(?:Apt|Apartment|Suite|Ste|Unit)\s*#?\d*)?(?:,\s*[A-Za-z\s]+)?(?:,\s*[A-Z]{{2}})?\s*\d{{5}}(?:-\d{{4}})?\b',
            r'P\.?O\.?\s*Box\s+\d+(?:,\s*[A-Za-z]+)?(?:,\s*[A-Z]{2})?\s*\d{5}(?:-\d{4})?',
        ]

        
        for pattern in address_patterns:
            matches = re.finditer(pattern, redacted_text, re.IGNORECASE)
            for match in matches:
                if not self.is_whitelisted(match.group()):
                    redacted_text = redacted_text.replace(match.group(), "█" * len(match.group()))
                    self.stats["addresses"] += 1

        # Redact using spaCy entities
        for ent in doc.ents:
            if ent.label_ in ["GPE", "LOC", "FAC"] and not self.is_whitelisted(ent.text):
                redacted_text = redacted_text.replace(ent.text, "█" * len(ent.text))
                self.stats["addresses"] += 1

        return redacted_text


    def get_synonyms(self, term):
        synonyms = set()
        for syn in wordnet.synsets(term):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name())
        synonyms.add(term + 's')
        return list(synonyms)
    
    def redact_concept(self, text, concepts):
        lines = text.split('\n')
        redacted_lines = []

        for line in lines:
            doc = self.nlp(line)
            redacted_line = line

            for concept in concepts:
                synonyms = self.get_synonyms(concept)
                terms_to_redact = [concept] + synonyms

                if concept not in self.stats["concepts"]:
                    self.stats["concepts"][concept] = 0

                for sent in doc.sents:
                    redactions_in_sentence = 0

                    for term in terms_to_redact:
                        matches = re.findall(r'\b' + re.escape(term) + r'\b', sent.text, re.IGNORECASE)
                        redactions_in_sentence += len(matches)

                    if redactions_in_sentence == 0:
                        sent_doc = self.nlp(sent.text)
                        if sent_doc.vector_norm:
                            for term in terms_to_redact:
                                term_doc = self.nlp(term)
                                if term_doc.vector_norm and sent_doc.similarity(term_doc) > 0.6:
                                    redactions_in_sentence += 1
                                    break

                    if redactions_in_sentence > 0:
                        start = sent.start_char
                        end = sent.end_char
                        redacted_sentence = '█' * (end - start)
                        redacted_line = redacted_line[:start] + redacted_sentence + redacted_line[end:]
                        self.stats["concepts"][concept] += redactions_in_sentence

            redacted_lines.append(redacted_line)

        return '\n'.join(redacted_lines)
        


    def process_file(self, file_path, flags, concepts):
        with open(file_path, 'r') as file:
            content = file.readlines()  

        redacted_content = []

        for line in content:
            if flags.names:
                line = self.redact_names(line)
            if flags.dates:
                line = self.redact_dates(line)
            if flags.phones:
                line = self.redact_phones(line)
            if flags.address:
                line = self.redact_address(line)
            if flags.emails:  
                line = self.redact_emails(line)  
            if concepts:
                line = self.redact_concept(line, concepts)
            
            redacted_content.append(line)  

        return ''.join(redacted_content)  



    def write_output(self, content, output_dir, file_name):
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{file_name}_censored")
        
        with open(output_path, 'w') as file:
            file.write(content)

    def write_stats(self, stats_location):
        stats_output = "\n".join([f"{key}: {value}" for key, value in self.stats.items()])
        
        if stats_location == 'stderr':
            print(stats_output)
        elif stats_location == 'stdout':
            print(stats_output)
        else:
            with open(stats_location, 'w') as file:
                file.write(stats_output)

def main():
    parser = argparse.ArgumentParser(description="Redact sensitive information from text files.")
    parser.add_argument("--input", nargs="+", required=True, help="Input glob pattern(s)")
    parser.add_argument("--names", action="store_true", help="Redact names")
    parser.add_argument("--dates", action="store_true", help="Redact dates")
    parser.add_argument("--phones", action="store_true", help="Redact phone numbers")
    parser.add_argument("--address", action="store_true", help="Redact addresses")
    parser.add_argument("--emails", action="store_true", help="Redact email addresses")
    parser.add_argument("--concept", action="append", help="Redact concepts")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--stats", required=True, help="Stats output location (file or stderr/stdout)")

    args = parser.parse_args()

    redactor = Redactor()


    for pattern in args.input:
        for file_path in glob.glob(pattern):
            try:
                file_name = os.path.basename(file_path)
                redacted_content = redactor.process_file(file_path, args, args.concept or [])
                redactor.write_output(redacted_content, args.output, file_name)
            except Exception as e:
                print(f"Error processing file {file_path}: {str(e)}")

    redactor.write_stats(args.stats)

if __name__ == "__main__":
    main()