# text_processor.py

def count_words(text):
    """Count the number of words in text"""
    return len(text.split())

def capitalize_words(text):
    """Capitalize the first letter of each word"""
    return text.title()

def reverse_text(text):
    """Reverse the text"""
    return text[::-1]

def get_word_count(text):
    """Get a dictionary with word frequency counts"""
    words = text.lower().split()
    word_count = {}
    for word in words:
        word_count[word] = word_count.get(word, 0) + 1
    return word_count

def contains_word(text, word):
    """Check if text contains a specific word (case-insensitive)"""
    return word.lower() in text.lower()
    
def find_longest_word(words):
    """Find the longest word in a list"""
    return max(words, key=len)

def filter_short_words(words, min_length):
    """Filter out words shorter than min_length"""
    result = []
    for word in words:
        if len(word) >= min_length:
            result.append(word)
    return result

def save_text_to_file(text, filepath):
    """Save text to a file"""
    with open(filepath, 'w') as f:
        f.write(text)

def read_text_from_file(filepath):
    """Read text from a file"""
    with open(filepath, 'r') as f:
        return f.read()

def count_sentences(text):
    """Count the number of sentences (separated by periods)"""
    sentences = text.split('.')
    count = 0
    for sentence in sentences:
        if sentence.strip():
            count += 1
    return count

def get_average_word_length(text):
    """Calculate average word length in text"""
    words = text.split()
    if not words:
        return 0
    total_length = 0
    for word in words:
        total_length += len(word)
    return total_length / len(words)

def remove_punctuation(text):
    """Remove common punctuation from text"""
    punctuation = '.,!?;:'
    for char in punctuation:
        text = text.replace(char, '')
    return text