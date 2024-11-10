#!/bin/bash

echo "Введите число"

read var

if [ $var -gt 0 ]; then
	var_from=1;
	while [ $var_from -le $var ]; do
		echo $var_from;
		var_from=$((var_from+1));
	done;
fi
