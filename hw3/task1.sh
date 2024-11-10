#!/bin/bash

ls -F

if [ -e $1 ]; then
	echo "File exists"
else
	echo "File doesn't exists"
fi

for filename in *; do
	ls -l $filename;
done
