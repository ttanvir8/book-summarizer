#!/usr/bin/env bash
git add .
git status
git commit -m "deploying..."
git status
git push origin main
