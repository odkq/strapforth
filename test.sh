#!/bin/bash
gforth test.fth -e bye > output-gforth.txt
./strapforth.py test.fth > output-strapforth.txt
diff -u output-gforth.txt output-strapforth.txt
result=$?
rm output-gforth.txt output-strapforth.txt

if [ $result -eq 0 ]; then
  echo "Output from gforth and strapforth is the same. Test PASSED"
  exit 0
else
  echo "Output from gforth and strapforth is the same. Test FAILED"
  exit 1
fi
