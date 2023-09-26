#!/bin/bash

# Use pgrep to get all python process ids and pass them to kill command
pids=$(pgrep -f python)

# Check if there are any python processes to kill
if [ -z "$pids" ]; then
    echo "No python processes found."
    exit 0
fi

# Kill python processes
echo "Killing python processes: $pids"
kill -9 $pids
