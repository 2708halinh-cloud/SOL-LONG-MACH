package hellocheck

import (
    "crypto/rand"
    "errors"
    "math/big"
)

// GeneratePrivateScalar returns secure key material in [1, secp256k1.N-1].
// This is NOT a wallet: obtaining a secp256k1 public key, WIF, an address,
// securing backups, and signing transactions require separately reviewed code.
// Never print private key material, never persist it automatically.
func GeneratePrivateScalar() ([32]byte, error) {
    var key [32]byte
    order, ok := new(big.Int).SetString(
        "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141", 16)
    if !ok { return key, errors.New("curve order unavailable") }
    n, err := rand.Int(rand.Reader, new(big.Int).Sub(order, big.NewInt(1)))
    if err != nil { return key, err }
    n.Add(n, big.NewInt(1))
    n.FillBytes(key[:])
    return key, nil
}
