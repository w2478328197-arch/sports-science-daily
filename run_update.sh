#!/bin/bash

# Get the directory where the script is stored
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Activate environment if needed, or just use python3
# Check for pip/python requirements
if ! python3 -c "import feedparser" &> /dev/null; then
    echo "Installing requirements..."
    pip3 install -r requirements.txt
fi

# Run the crawler
# Default to 3 days lookback for daily runs
DAYS=3

# If valid argument provided, use it
if [[ "$1" =~ ^[0-9]+$ ]]; then
    DAYS=$1
fi

echo "Running Daily Sports Science & Tech Update (Last $DAYS days)..."
python3 daily_sports_update.py --days $DAYS

echo ""
echo "Done! Check the markdown files in $DIR"
