#!/bin/bash

git add d8698dc6486a096a6de364a141z78646.json
git commit -m "update config"
git push
python3 send_email_notification.py
