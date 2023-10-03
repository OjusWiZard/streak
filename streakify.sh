#!/bin/bash

cd $(dirname "$0")

STREAKFILE='.streak'

# HITS=$(($(($RANDOM%3))+1))
HITS=1

for i in `seq $HITS`
do
    echo `date` >> $STREAKFILE

    RANDOM_MSG="$(curl -s https://raw.githubusercontent.com/ngerakines/commitment/main/commit_messages.txt | shuf -n 1)"
    git commit -a -m "$RANDOM_MSG"
done
git push

echo "Congratulations, you just kept your commit streak going!"

