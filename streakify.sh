#!/usr/bin/env bash

STREAKFILE='.streak'

HITS=$(($(($RANDOM%3))+1))

for i in `seq $HITS`
do
    echo `date` >> $STREAKFILE
    git commit -a -m "update streak for `date`"
done
git push

echo 'Congratulations, you just kept your streak going'
