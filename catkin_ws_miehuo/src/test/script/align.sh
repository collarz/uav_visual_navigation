#!/bin/bash
while(true)
do
    python3 align.py iris 0 0 0 0&
    python3 align.py iris 1 2.5 0 0&
    python3 align.py iris 2 -2.5 0 0
done