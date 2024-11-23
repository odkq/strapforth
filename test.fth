\ Test some forth features. To test, compare output of strapforth with
\ the output of gforth test.fth -e yes
3 2 56 . .s +
\ Some arithmetic
5 4 + . 6 7 * . 234 50 - . 12345 34 / .
\ Stack manipulation
1 2 3 4 tuck .s over .s 2 roll .s 3 pick .s
\ Define new words
: square ( n -- n ) dup * ; : cube square dup * ;
\ Introspection
see square 5 cube . see cube
