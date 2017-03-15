#!/bin/bash

source setup.sh

rm -rf ../Output/$1/*
./MadAnalysis5job ../Input/$1
