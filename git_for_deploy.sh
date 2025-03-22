#!/usr/bin/env bash
git add .
git status
git commit -m "deploying with changed code for optimization"
git status
git push origin main
