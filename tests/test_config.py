# tests/test_config.py
"""
Test configuration and constants for real library usage.
This replaces command line arguments and hardcoded values with configurable parameters.
"""
import os
from pathlib import Path

# Test data paths
TEST_DATA_DIR = Path(__file__).parent / "test_data"
TEST_EMBEDDINGS_DIR = Path(__file__).parent / "test_embeddings"
TEST_OUTPUT_DIR = Path(__file__).parent / "test_output"

# Embedding model configuration
DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"  # Lightweight model for testing
EMBEDDING_DIMENSION = 384  # Dimension for all-MiniLM-L6-v2
TEST_DEVICE = "cpu"  # Always use CPU for tests to ensure consistency

# Index configuration
DEFAULT_CHUNK_SIZE = 512
DEFAULT_OVERLAP = 50
DEFAULT_TOP_K = 10

# Test document content
SAMPLE_DOCUMENTS = [
    {
        "name": "python_basics.md",
        "content": """# Python Basics

Python is a high-level programming language known for its simplicity and readability.

## Variables and Data Types
- Strings: text data
- Integers: whole numbers
- Floats: decimal numbers
- Lists: ordered collections
- Dictionaries: key-value pairs

## Functions
Functions are reusable blocks of code that perform specific tasks.

```python
def greet(name):
    return f"Hello, {name}!"
```

## Control Flow
Python supports if statements, loops, and exception handling.
""",
        "metadata": {"category": "programming", "difficulty": "beginner"}
    },
    {
        "name": "machine_learning.md", 
        "content": """# Machine Learning Overview

Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience.

## Types of Machine Learning
1. Supervised Learning: Learning with labeled data
2. Unsupervised Learning: Finding patterns in unlabeled data  
3. Reinforcement Learning: Learning through rewards and penalties

## Common Algorithms
- Linear Regression
- Decision Trees
- Neural Networks
- Support Vector Machines
- K-Means Clustering

## Applications
Machine learning is used in recommendation systems, image recognition, natural language processing, and autonomous vehicles.
""",
        "metadata": {"category": "ai", "difficulty": "intermediate"}
    },
    {
        "name": "web_development.html",
        "content": """<!DOCTYPE html>
<html>
<head>
    <title>Web Development Guide</title>
</head>
<body>
    <header>
        <h1>Modern Web Development</h1>
        <nav>
            <ul>
                <li><a href="#frontend">Frontend</a></li>
                <li><a href="#backend">Backend</a></li>
            </ul>
        </nav>
    </header>
    
    <main>
        <section id="frontend">
            <h2>Frontend Technologies</h2>
            <p>Frontend development involves creating user interfaces using:</p>
            <ul>
                <li><strong>HTML</strong>: Structure and content</li>
                <li><strong>CSS</strong>: Styling and layout</li>
                <li><strong>JavaScript</strong>: Interactivity and behavior</li>
            </ul>
            
            <h3>Popular Frameworks</h3>
            <ul>
                <li>React</li>
                <li>Vue.js</li>
                <li>Angular</li>
            </ul>
        </section>
        
        <section id="backend">
            <h2>Backend Development</h2>
            <p>Backend development focuses on server-side logic, databases, and APIs.</p>
            <pre><code>
# Example API endpoint
@app.route('/api/users')
def get_users():
    return jsonify(users)
            </code></pre>
        </section>
    </main>
    
    <footer>
        <p>© 2024 Web Development Guide</p>
    </footer>
</body>
</html>""",
        "metadata": {"category": "web", "difficulty": "intermediate"}
    }
]

# Test queries for search validation
TEST_QUERIES = [
    "Python functions and variables",
    "machine learning algorithms", 
    "HTML CSS JavaScript",
    "supervised learning",
    "web development frameworks"
]

# Expected search results (for validation)
EXPECTED_RESULTS = {
    "Python functions and variables": ["python_basics.md"],
    "machine learning algorithms": ["machine_learning.md"],
    "HTML CSS JavaScript": ["web_development.html"],
    "supervised learning": ["machine_learning.md"],
    "web development frameworks": ["web_development.html"]
}

def ensure_test_directories():
    """Create test directories if they don't exist."""
    TEST_DATA_DIR.mkdir(exist_ok=True, parents=True)
    TEST_EMBEDDINGS_DIR.mkdir(exist_ok=True, parents=True) 
    TEST_OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

def cleanup_test_directories():
    """Clean up test directories after tests."""
    import shutil
    for directory in [TEST_DATA_DIR, TEST_EMBEDDINGS_DIR, TEST_OUTPUT_DIR]:
        if directory.exists():
            shutil.rmtree(directory)

def get_model_name():
    """Get model name from environment or use default."""
    return os.getenv("TEST_MODEL_NAME", DEFAULT_MODEL_NAME)

def get_device():
    """Get device from environment or use default."""
    return os.getenv("TEST_DEVICE", TEST_DEVICE)

def should_skip_slow_tests():
    """Check if slow tests should be skipped."""
    return os.getenv("SKIP_SLOW_TESTS", "false").lower() == "true"