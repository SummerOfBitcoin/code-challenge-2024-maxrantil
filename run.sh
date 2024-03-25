#!/bin/bash

# Define the path to the virtual environment directory
VENV_DIR="env"

# Ensure Python 3 and pip are installed
if ! command -v python3 &> /dev/null || ! command -v pip &> /dev/null; then
    echo "Python 3 or pip could not be found. Please install them before running this script."
    exit 1
fi

# Install virtualenv if it's not installed
if ! python3 -m pip show virtualenv &> /dev/null; then
    echo "Installing virtualenv..."
    python3 -m pip install virtualenv
fi

# Check if the virtual environment directory exists
if [ ! -d "${VENV_DIR}" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "${VENV_DIR}"
    echo "Virtual environment created."
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source "${VENV_DIR}"/bin/activate

# Install dependencies from requirements.txt
echo "Installing dependencies..."
pip install -r requirements.txt

# Run your Python script
echo "Running script..."
python src/main.py

# Deactivate the virtual environment
deactivate
echo "Script execution completed."
