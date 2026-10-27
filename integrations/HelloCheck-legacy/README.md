# HelloCheck / HelloBitcoin — Go, Bitcoin TestNet

SOURCE_DIRECT from Hà Linh: [INBOX_SOURCE_DIRECT_20261023.md](INBOX_SOURCE_DIRECT_20261023.md). Original `keys.go` / `transaction.go` snippets preserved there; runnable derived code is kept separately in this folder.

**What actually works (offline):** Base58Check decoding for legacy TestNet P2PKH (version `0x6f`), deterministic **unsigned** transaction serialization, explicit UTXO amount/fee/change validation, Go regression tests, secure 32-byte secp256k1 scalar candidate generation using `crypto/rand` without printing secret values.

**Not completed:** public-key derivation and a fully usable wallet, WIF generation, UTXO retrieval, signing, fee estimation, broadcasting and TestNet transaction confirmation. No real coins are spent. These remain OPEN until exact chain/network readback.

Run from this directory:

```sh
go test ./...
go run ./cmd/hellocheck -txid 7756bf4ed3b495adb63e05c02398e799c471b885d10523028b6e1b10f0ae181f -vout 1 -input-sats 25100000 -to msj42CCGruhRsFrGATiUuh25dtxYtnpbTx -send-sats 25000000 -fee-sats 10000 -change mujf6HNVrAFUX2gjNgirTWyxaT7XzeKUrj
```

The CLI prints only an **unsigned transaction template**, never a broadcastable signed transaction. The 25,100,000 input amount is a *synthetic example*, **not** a verified UTXO. No network access or wallet balance is implied.

The user's legacy source used `math/rand` and a `secp256k1-go` import; the maintained key source uses `crypto/rand`. The original commented-out code also confused the unlocking script (`scriptSig`) with the destination P2PKH locking script and did not account for UTXO amount, fee, change or correct endian encoding.

The Android app `com.studio.hellohabit` belongs to a separate T005 branch; it is not the HelloCheck/Bitcoin project.
