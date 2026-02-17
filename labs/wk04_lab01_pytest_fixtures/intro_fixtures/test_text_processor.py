# test_text_processor.py
import pytest
from text_processor import count_words, capitalize_words, reverse_text,get_word_count, contains_word, find_longest_word, filter_short_words,save_text_to_file, read_text_from_file, count_sentences, get_average_word_length, remove_punctuation

@pytest.fixture
def sample_text():
    """Provide sample text for tests"""
    return "the quick brown fox"
    

def test_count_words(sample_text):
    # TODO: Use the sample_text fixture parameter
    assert count_words(sample_text) == 4
    pass

def test_capitalize_words(sample_text):
    # TODO: Use the sample_text fixture parameter
    assert capitalize_words(sample_text) == "The Quick Brown Fox"
    pass

def test_reverse_text(sample_text):
    # TODO: Use the sample_text fixture parameter
    assert reverse_text("xof nworb kciuq eht")
    pass

@pytest.fixture
def paragraph():
    return "Python is great. Python is powerful. Python is fun."

@pytest.fixture
def search_word():
    return "python"

def test_get_word_count(paragraph):
    counts = get_word_count(paragraph)
    expected = {'python': 3, 'is': 3, 'great.': 1, 'powerful.': 1, 'fun.': 1}
    assert counts == expected

def test_contains_word(paragraph, search_word):
    assert contains_word(paragraph, search_word) is True

@pytest.fixture
def word_list():
    """Provide a list of words for testing"""
    # TODO: Return a list: ["cat", "elephant", "dog", "butterfly", "ant"]
    pass

def test_find_longest_word(word_list):
    # TODO: Test that find_longest_word returns "butterfly"
    pass

def test_filter_short_words(word_list):
    # TODO: Test that filter_short_words(word_list, 4) returns ["elephant", "butterfly"]
    pass

def test_save_text_to_file(tmp_path):
    """Test saving text to a file"""
    # tmp_path is a built-in fixture that provides a temporary directory
    
    # TODO: Create a file path: tmp_path / "test.txt"
    # TODO: Save "Hello, World!" to that file using save_text_to_file
    # TODO: Read the file directly and assert it contains "Hello, World!"
    pass

def test_read_text_from_file(tmp_path):
    """Test reading text from a file"""
    # TODO: Create a file path: tmp_path / "input.txt"
    # TODO: Write "Test content" to the file (use file_path.write_text())
    # TODO: Use read_text_from_file to read it
    # TODO: Assert the result is "Test content"
    pass

@pytest.fixture
def greeting():
    """Provide a greeting"""
    # TODO: Return "Hello"
    pass

@pytest.fixture
def name():
    """Provide a name"""
    # TODO: Return "Alice"
    pass

@pytest.fixture
def full_greeting(greeting, name):
    """Combine greeting and name"""
    # TODO: Return f"{greeting}, {name}!"
    # Example: "Hello, Alice!"
    pass

def test_full_greeting(full_greeting):
    # TODO: Assert full_greeting equals "Hello, Alice!"
    pass

@pytest.fixture
def essay():
    """Provide a multi-sentence essay"""
    # TODO: Return "The cat sat. The dog ran. The bird flew."
    pass

@pytest.fixture
def simple_sentence():
    """Provide a simple sentence with punctuation"""
    # TODO: Return "Hello, world! How are you?"
    pass

@pytest.fixture
def cleaned_text():
    """Provide text without punctuation"""
    # TODO: Return "Hello world How are you"
    pass

def test_count_sentences(essay):
    # TODO: Test that count_sentences returns 3
    pass

def test_get_average_word_length(essay):
    # TODO: Test that average word length is approximately 3.0
    # Hint: Words are ["The", "cat", "sat", "The", "dog", "ran", "The", "bird", "flew"]
    # Average = (3+3+3+3+3+3+3+4+4) / 9 = 29/9 ≈ 3.22
    pass

def test_remove_punctuation(simple_sentence, cleaned_text):
    # TODO: Test that remove_punctuation(simple_sentence) returns cleaned_text
    pass