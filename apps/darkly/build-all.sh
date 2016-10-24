#!/bin/bash

for app in $(find . -mindepth 1 -maxdepth 1 -type d)
do
  echo $app
  echo "Building $app"
  cd $app
  make clean
  make
  cd ..
done
