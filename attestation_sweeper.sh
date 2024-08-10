#! /bin/bash 


DIRECTORY="/src/app/attestations"
LOG_FILE="/src/.attestation_sweeper.log"

REMOVE_FILE() {
    echo "removing $1 on $(date +"%Y-%m-%d %H:%M:%S.%3N")" >> "$LOG_FILE"
    sudo rm "$1"
}

LOOP_THRU_DIR() {
    for file in "$1"/*; do
        if [[ -f "$file" ]]; then
            REMOVE_FILE "$file"
        elif [[ -d "$file" ]]; then
            LOOP_THRU_DIR "$file"
        fi
    done
}

# Check if the log file exists
if [[ ! -e "$LOG_FILE" ]]; then
    touch "$LOG_FILE"
fi

# Check if the target is a directory
if [[ ! -d "$DIRECTORY" ]]; then
    exit 1
fi

# Loop through items in the target directory
LOOP_THRU_DIR "$DIRECTORY"
