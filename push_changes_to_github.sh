#!/bin/bash

while true; do
    git add .
    git commit -m "config update by telegram bot"
    git push
    sleep 360
done
