#!/bin/bash
# Shell script to run tests with different configurations

echo "========================================"
echo "Library Management System - Test Runner"
echo "========================================"
echo

case "$1" in
    all)
        echo "Running ALL tests..."
        pytest -v
        ;;
    coverage)
        echo "Running tests with coverage..."
        pytest --cov=. --cov-report=html --cov-report=term-missing
        echo
        echo "Coverage report generated in htmlcov/index.html"
        ;;
    accounts)
        echo "Running accounts tests..."
        pytest accounts/tests.py -v
        ;;
    books)
        echo "Running books tests..."
        pytest books/tests.py -v
        ;;
    loans)
        echo "Running loans tests..."
        pytest loans/tests.py -v
        ;;
    quick)
        echo "Running quick tests (no coverage)..."
        pytest -v --no-cov
        ;;
    *)
        echo "Usage: ./run_tests.sh [option]"
        echo
        echo "Options:"
        echo "  all       - Run all tests"
        echo "  coverage  - Run tests with coverage report"
        echo "  accounts  - Run only accounts tests"
        echo "  books     - Run only books tests"
        echo "  loans     - Run only loans tests"
        echo "  quick     - Run tests without coverage"
        echo
        echo "Example: ./run_tests.sh coverage"
        ;;
esac
