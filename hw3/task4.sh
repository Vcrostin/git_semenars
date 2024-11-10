#!/bin/bash

hello_ () {
	HelloWorld="Hello, $1";
}

hello_ "world"
echo $HelloWorld

sum () {
	return $(($1 + $2));
}

sum 1 2
echo $?
