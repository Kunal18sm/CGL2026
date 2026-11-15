@echo off
title SSC CGL 2026 Intelligence & Practice Portal
echo Starting SSC CGL 2026 Portal on http://localhost:8080...
start "" "http://localhost:8080"
python -m http.server 8080
pause
