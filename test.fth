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
( see cube )
\ As in 0, 0 is true and != 0 is false
10 10 = . 12 53 = .
12 10 > . 12 12 > .
10 10 <> . 12 53 <> .
\ test if..else..then
: ?>50 ( n -- n ) dup 50 > if 1111 else 2222 then ;
100 ?>50 . 40 ?>50 .
\ Test trailing whitespaces
10  20  30
hex
10 10 + .
include test2.fth
test2 .
