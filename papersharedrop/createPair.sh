#!/bin/bash
rm addresses
for I in `seq 1 10`
do
 ret=$(./bts_create_key)
 wif=$(echo "${ret}"| grep "WIF" | sed 's/^.*: //')
 add=$(echo "${ret}"| grep "bts" | sed 's/^.*: //')
 pub=$(echo "${ret}"| grep "pub" | sed 's/^.*: //')
 echo "${pub};${wif};${add}" >> addresses
 qrencode -o qr/${pub}.png -lL -tpng -8 ${wif}
done
