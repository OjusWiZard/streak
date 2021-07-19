#!/usr/bin/env bash

STREAKFILE='.streak'

HITS=$(($(($RANDOM%3))+1))

cd /home/Tanyx01/streak/

for i in `seq $HITS`
do
    echo `date` >> $STREAKFILE
    git commit -a -m "update streak for `date`"
done
git push

echo 'Congratulations, you just kept your streak going'
