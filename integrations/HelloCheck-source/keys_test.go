package hellocheck

import (
    "math/big"
    "testing"
)
func TestSecureScalarWithinSecp256k1Range(t *testing.T) {
    n,_:=new(big.Int).SetString(
        "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141",16)
    a,err:=GeneratePrivateScalar()
    if err!=nil {t.Fatal(err)}
    b,err:=GeneratePrivateScalar()
    if err!=nil {t.Fatal(err)}
    ai:=new(big.Int).SetBytes(a[:]);bi:=new(big.Int).SetBytes(b[:])
    if ai.Sign()<=0 || ai.Cmp(n)>=0 || bi.Sign()<=0 || bi.Cmp(n)>=0 {
        t.Fatal("scalar outside secp256k1 order")
    }
    if ai.Cmp(b)==0 {t.Fatal("identical secure random scalars")}
}
