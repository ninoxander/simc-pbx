#!/usr/bin/env bash
set -e

# Base
mkdir -p asterisk/config golang-middleware python-ai

# Crear archivos root
touch docker-compose.yml .gitignore

# Asterisk
touch asterisk/config/pjsip.conf asterisk/config/extensions.conf asterisk/config/rtp.conf

# Golang Middleware
touch golang-middleware/Dockerfile golang-middleware/go.mod golang-middleware/main.go

# Python
touch python-ai/Dockerfile python-ai/requirements.txt python-ai/main.py