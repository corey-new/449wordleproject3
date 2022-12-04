#!/bin/sh

echo "Setting up file structure..."
mkdir -p ./var/primary/mount && mkdir -p ./var/primary/data
mkdir -p ./var/secondary/mount && mkdir -p ./var/secondary/data
mkdir -p ./var/tertiary/mount && mkdir -p ./var/tertiary/data