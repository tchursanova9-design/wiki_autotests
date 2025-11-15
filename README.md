# Playwright Tests

A minimal Python project using Playwright and pytest for browser automation testing.

## Requirements

- Python 3.11 or higher

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install
```

## Running Tests

Run all tests with verbose output:
```bash
pytest -v
```

Run a specific test file:
```bash
pytest tests/test_wikipedia_oxygen.py -v
```

## Project Structure

```
.
├── requirements.txt
├── README.md
└── tests/
    └── test_wikipedia_oxygen.py
```

