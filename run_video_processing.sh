#!/bin/bash

# Number of times to run the function
RUNS=10

# Output log file
LOG_FILE="video_processing_output.log"

# Clear the previous log file if exists
> "$LOG_FILE"

echo "Running video-processing function $RUNS times..."
echo "----------------------------------------" | tee -a "$LOG_FILE"

for i in $(seq 1 $RUNS); do
    echo "Run #$i:" | tee -a "$LOG_FILE"
    
    # Capture the start time
    START_TIME=$(date +%s%3N)
    
    # Call the function and save the output
    RESPONSE=$(curl -s -X POST http://127.0.0.1:8080/function/video-processing)
    
    # Capture the end time
    END_TIME=$(date +%s%3N)
    
    # Calculate the execution time
    EXECUTION_TIME=$((END_TIME - START_TIME))
    
    # Log the response and execution time
    echo "Response: $RESPONSE" | tee -a "$LOG_FILE"
    echo "Execution Time: ${EXECUTION_TIME}ms" | tee -a "$LOG_FILE"
    echo "----------------------------------------" | tee -a "$LOG_FILE"
    
    # Optional: Add a short delay between runs to avoid overloading
    sleep 2
done

echo "All runs completed. Check $LOG_FILE for details."
