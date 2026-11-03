package main

import (
    "encoding/hex"
    "flag"
    "fmt"
    "math"
    "os"

    "hellocheck"
)

// Only offline serialization. No wallet keys, network, signing or broadcasting.
func main() {
    txid := flag.String("txid", "", "Observed previous transaction ID (32-byte hex)")
    vout := flag.Uint("vout", 0, "Previous output index")
    input := flag.Uint64("input-sats", 0, "Observed input output value in satoshis")
    to := flag.String("to", "", "TestNet P2PKH destination address")
    send := flag.Uint64("send-sats", 0, "Amount for destination in satoshis")
    fee := flag.Uint64("fee-sats", 0, "Explicit fee in satoshis")
    changeAddr := flag.String("change", "", "TestNet P2PKH change address (required when change exists)")
    flag.Parse()
    if *vout > math.MaxUint32 {
        fmt.Fprintln(os.Stderr, "vout outside uint32")
        os.Exit(2)
    }
    draft := hellocheck.Draft{
        Input: hellocheck.UnsignedInput{TxID:*txid,Vout:uint32(*vout),UTXOSatoshis:*input},
        Destination: hellocheck.Payment{Address:*to,Satoshis:*send},
        FeeSatoshis:*fee,
    }
    if *changeAddr != "" {
        if *input < *send || *fee > *input - *send {
            fmt.Fprintln(os.Stderr, "not enough input value")
            os.Exit(2)
        }
        draft.Change=&hellocheck.Payment{Address:*changeAddr,Satoshis:*input-*send-*fee}
    }
    result,err := hellocheck.BuildUnsignedTestnetP2PKH(draft)
    if err != nil {
        fmt.Fprintln(os.Stderr, "UNSIGNED_BUILD_FAILED:", err)
        os.Exit(2)
    }
    fmt.Println("NOT_SIGNED_NOT_BROADCASTABLE")
    fmt.Println(hex.EncodeToString(result))
}
