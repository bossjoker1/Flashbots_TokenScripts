#!/bin/bash

proxychains -q python3 bundle.py &
proxychains -q python3 bundle1.py &
proxychains -q python3 bundle2.py &

wait
echo "All scripts have completed."
