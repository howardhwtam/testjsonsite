#!/bin/bash

while true; do
    date
    git add .
    git commit -m "config update by telegram bot"
    git push
    sleep 3600
done
