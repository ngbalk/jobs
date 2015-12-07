#!/bin/bash
python jpmc-email-parser.py
git add .
git commit -am "newly injested material"
git push origin HEAD:master
