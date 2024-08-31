#!/bin/bash

if [ "$1" == "" ]; then
    bash
else
    curl -o $1 "https://fileserver-2osynaaqfa-uc.a.run.app/download?filename=/app/files/$1"
    tar -xf $1
    rm $1
    clear
    bash
fi
