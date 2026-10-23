package hellocheck

// Minimal, dependency-free Bitcoin TestNet legacy P2PKH unsigned transaction
// materializer. It cannot sign or broadcast a Bitcoin transaction.
// No key material or outgoing network operations are performed by this package.

import (
    "bytes"
    "crypto/sha256"
    "encoding/binary"
    "encoding/hex"
    "errors"
    "fmt"
    "math/big"
    "strings"
)

const base58Alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
const maxSatoshis uint64 = 21000000 * 100000000

type UnsignedInput struct {
    TxID string
    Vout uint32
    UTXOSatoshis uint64
}
type Payment struct {
    Address string
    Satoshis uint64
}
type Draft struct {
    Input UnsignedInput
    Destination Payment
    Change *Payment
    FeeSatoshis uint64
}

// DecodeTestnetP2PKH enforces Base58Check checksum AND version 0x6f;
// a Base58 number is not the P2PKH 20-byte pubkey hash.
func DecodeTestnetP2PKH(address string) ([20]byte, error) {
    var hash [20]byte
    if address == "" {
        return hash, errors.New("empty destination address")
    }
    amount := big.NewInt(0)
    radix := big.NewInt(58)
    for _, runeValue := range address {
        digit := strings.IndexRune(base58Alphabet, runeValue)
        if digit < 0 { return hash, errors.New("invalid Base58 character") }
        amount.Mul(amount, radix)
        amount.Add(amount, big.NewInt(int64(digit)))
    }
    decoded := amount.Bytes()
    for _, ch := range address {
        if ch != '1' { break }
        decoded = append([]byte{0}, decoded...)
    }
    if len(decoded) != 25 {
        return hash, fmt.Errorf("invalid decoded address length: %d", len(decoded))
    }
    check := sha256.Sum256(decoded[:21])
    check = sha256.Sum256(check[:])
    if !bytes.Equal(check[:4], decoded[21:]) {
        return hash, errors.New("Base58Check checksum mismatch")
    }
    if decoded[0] != 0x6f {
        return hash, errors.New("address is not a TestNet P2PKH address")
    }
    copy(hash[:], decoded[1:21])
    return hash, nil
}

func p2pkhScript(hash [20]byte) []byte {
    result := []byte{0x76, 0xa9, 0x14} // OP_DUP OP_HASH160 PUSH20
    result = append(result, hash[:]...)
    result = append(result, 0x88, 0xac) // OP_EQUALVERIFY OP_CHECKSIG
    return result
}
func compactSize(buffer *bytes.Buffer, number uint64) {
    switch {
    case number < 0xfd:
        buffer.WriteByte(byte(number))
    case number <= 0xffff:
        buffer.WriteByte(0xfd)
        _ = binary.Write(buffer, binary.LittleEndian, uint16(number))
    case number <= 0xffffffff:
        buffer.WriteByte(0xfe)
        _ = binary.Write(buffer, binary.LittleEndian, uint32(number))
    default:
        buffer.WriteByte(0xff)
        _ = binary.Write(buffer, binary.LittleEndian, number)
    }
}
func writeOutput(buffer *bytes.Buffer, payment Payment) error {
    if payment.Satoshis == 0 || payment.Satoshis > maxSatoshis {
        return errors.New("invalid output value")
    }
    hash, err := DecodeTestnetP2PKH(payment.Address)
    if err != nil { return err }
    _ = binary.Write(buffer, binary.LittleEndian, payment.Satoshis)
    script := p2pkhScript(hash)
    compactSize(buffer, uint64(len(script)))
    _, _ = buffer.Write(script)
    return nil
}

// BuildUnsignedTestnetP2PKH constructs only an UNSIGNED transaction template.
// It has an empty scriptSig and must never be passed to broadcast as final tx.
// Explicit input value, fee and change prevent accidental silent fee overpayment.
func BuildUnsignedTestnetP2PKH(d Draft) ([]byte, error) {
    txid, err := hex.DecodeString(d.Input.TxID)
    if err != nil || len(txid) != 32 {
        return nil, errors.New("input txid must be 32-byte hex")
    }
    if d.Input.UTXOSatoshis == 0 || d.Input.UTXOSatoshis > maxSatoshis {
        return nil, errors.New("invalid observed input UTXO amount")
    }
    if d.Destination.Satoshis == 0 || d.Destination.Satoshis > d.Input.UTXOSatoshis {
        return nil, errors.New("invalid destination amount")
    }
    if d.FeeSatoshis > d.Input.UTXOSatoshis - d.Destination.Satoshis {
        return nil, errors.New("fee exceeds available value")
    }
    remainder := d.Input.UTXOSatoshis - d.Destination.Satoshis - d.FeeSatoshis
    if d.Change == nil && remainder != 0 {
        return nil, errors.New("change must be specified; no implicit mining fee")
    }
    if d.Change != nil && (d.Change.Satoshis == 0 || d.Change.Satoshis != remainder) {
        return nil, errors.New("change output must equal exact remaining satoshis")
    }
    outputCount := uint64(1)
    if d.Change != nil { outputCount++ }
    var buffer bytes.Buffer
    _ = binary.Write(&buffer, binary.LittleEndian, uint32(1)) // version
    compactSize(&buffer, 1) // input count
    for i := len(txid)-1; i >= 0; i-- { buffer.WriteByte(txid[i]) } // previous txid LE
    _ = binary.Write(&buffer, binary.LittleEndian, d.Input.Vout)
    compactSize(&buffer, 0) // empty scriptSig: not signed
    _ = binary.Write(&buffer, binary.LittleEndian, uint32(0xffffffff))
    compactSize(&buffer, outputCount)
    if err := writeOutput(&buffer, d.Destination); err != nil { return nil, err }
    if d.Change != nil {
        if err := writeOutput(&buffer, *d.Change); err != nil { return nil, err }
    }
    _ = binary.Write(&buffer, binary.LittleEndian, uint32(0)) // locktime
    return buffer.Bytes(), nil
}
