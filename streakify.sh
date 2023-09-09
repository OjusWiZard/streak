#!/bin/bash

STREAKFILE='.streak'

HITS=$(($(($RANDOM%3))+1))

cd $(pwd)

for i in `seq $HITS`
do
    echo `date` >> $STREAKFILE
    git commit -a -m "$(curl -s https://whatthecommit.com/index.txt)"
done
git push

echo "Congratulations, you just kept your commit streak going"