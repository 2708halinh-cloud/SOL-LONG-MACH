package hellocheck

import (
 "bytes"
 "encoding/binary"
 "encoding/hex"
 "errors"
 "fmt"
 "crypto/sha256"
 "golang.org/x/crypto/ripemd160"

 secp "github.com/decred/dcrd/dcrec/secp256k1/v4"
 "github.com/decred/dcrd/dcrec/secp256k1/v4/ecdsa"
)
const MaxBitcoinSatoshis uint64=21000000*100000000
const MinimumChangeSatoshis uint64=546
type UTXO struct {
 TXID string // Big-endian hex as displayed by a block explorer.
 Vout uint32
 ValueSatoshis uint64 // Caller must verify this from a real trusted TestNet node.
}
type Payment struct {
 Destination string // TestNet legacy P2PKH address only.
 AmountSatoshis uint64
 FeeSatoshis uint64
 ChangeAddress string // Required if input value > amount+fee.
}
func put32(b *bytes.Buffer,n uint32){_ = binary.Write(b,binary.LittleEndian,n)}
func put64(b *bytes.Buffer,n uint64){_ = binary.Write(b,binary.LittleEndian,n)}
func writeVarInt(b *bytes.Buffer,n uint64){
 switch {
 case n<0xfd:b.WriteByte(byte(n))
 case n<=0xffff:b.WriteByte(0xfd);_ = binary.Write(b,binary.LittleEndian,uint16(n))
 case n<=0xffffffff:b.WriteByte(0xfe);put32(b,uint32(n))
 default:b.WriteByte(0xff);put64(b,n)
 }
}
// DraftUnsigned builds a one-input, one/two-output legacy Bitcoin transaction.
// It is NOT signed, NOT broadcast and does not verify the supplied UTXO.
func DraftUnsigned(input UTXO,p Payment)([]byte,error){
 txid,err:=hex.DecodeString(input.TXID)
 if err!=nil||len(txid)!=32{return nil,errors.New("TXID must be 64 hex characters")}
 if input.ValueSatoshis==0||input.ValueSatoshis>MaxBitcoinSatoshis{
  return nil,errors.New("invalid input value")}
 if p.AmountSatoshis==0||p.AmountSatoshis>MaxBitcoinSatoshis{
  return nil,errors.New("invalid output value")}
 if p.FeeSatoshis==0 || p.AmountSatoshis>input.ValueSatoshis ||
    p.FeeSatoshis>input.ValueSatoshis-p.AmountSatoshis{
  return nil,errors.New("invalid fee or insufficient UTXO value")
 }
 script,err:=P2PKHScript(p.Destination)
 if err!=nil{return nil,fmt.Errorf("destination: %w",err)}
 change:=input.ValueSatoshis-p.AmountSatoshis-p.FeeSatoshis
 var changeScript []byte
 if change>0 {
  if change<MinimumChangeSatoshis{return nil,errors.New("change would be dust")}
  if p.ChangeAddress=="" {return nil,errors.New("explicit TestNet change address required")}
  changeScript,err=P2PKHScript(p.ChangeAddress)
  if err!=nil{return nil,fmt.Errorf("change address: %w",err)}
 }
 var b bytes.Buffer
 put32(&b,1) // version is FOUR bytes, little endian
 writeVarInt(&b,1)
 for i:=31;i>=0;i-- {b.WriteByte(txid[i])}
 put32(&b,input.Vout)
 writeVarInt(&b,0) // unsigned scriptSig MUST be empty
 put32(&b,0xffffffff)
 nOutputs:=uint64(1);if change>0 {nOutputs++}
 writeVarInt(&b,nOutputs)
 put64(&b,p.AmountSatoshis);writeVarInt(&b,uint64(len(script)));b.Write(script)
 if change>0 {put64(&b,change);writeVarInt(&b,uint64(len(changeScript)));b.Write(changeScript)}
 put32(&b,0) // locktime
 return b.Bytes(),nil
}

// serializeLegacy is shared by the unsigned skeleton, signing preimage, and
// signed transaction. In signing preimage the input script is the prevout
// scriptPubKey; on wire it is the unlocking scriptSig.
func serializeLegacy(input UTXO,p Payment,inputScript []byte)([]byte,error){
 txid,err:=hex.DecodeString(input.TXID)
 if err!=nil||len(txid)!=32{return nil,errors.New("TXID must be 64 hex characters")}
 if input.ValueSatoshis==0||input.ValueSatoshis>MaxBitcoinSatoshis{
  return nil,errors.New("invalid input value")}
 if p.AmountSatoshis==0||p.AmountSatoshis>MaxBitcoinSatoshis{
  return nil,errors.New("invalid output value")}
 if p.FeeSatoshis==0||p.AmountSatoshis>input.ValueSatoshis||
 p.FeeSatoshis>input.ValueSatoshis-p.AmountSatoshis{
  return nil,errors.New("fee invalid or input insufficient")
 }
 outputScript,err:=P2PKHScript(p.Destination)
 if err!=nil{return nil,err}
 change:=input.ValueSatoshis-p.AmountSatoshis-p.FeeSatoshis
 var changeScript []byte
 if change!=0{
  if change<MinimumChangeSatoshis{return nil,errors.New("dust change is prohibited")}
  if p.ChangeAddress==""{return nil,errors.New("explicit change address required")}
  changeScript,err=P2PKHScript(p.ChangeAddress)
  if err!=nil{return nil,err}
 }
 var b bytes.Buffer
 put32(&b,1)
 writeVarInt(&b,1)
 for i:=31;i>=0;i--{b.WriteByte(txid[i])}
 put32(&b,input.Vout)
 writeVarInt(&b,uint64(len(inputScript)))
 b.Write(inputScript)
 put32(&b,0xffffffff)
 outputs:=uint64(1);if change!=0{outputs=2}
 writeVarInt(&b,outputs)
 put64(&b,p.AmountSatoshis)
 writeVarInt(&b,uint64(len(outputScript)));b.Write(outputScript)
 if change!=0{
  put64(&b,change);writeVarInt(&b,uint64(len(changeScript)));b.Write(changeScript)
 }
 put32(&b,0)
 return b.Bytes(),nil
}
func hash160Compressed(pubkey []byte)([]byte,error){
 first:=sha256.Sum256(pubkey)
 h:=ripemd160.New()
 if _,err:=h.Write(first[:]);err!=nil{return nil,err}
 return h.Sum(nil),nil
}
// SignLegacyTestnetP2PKH signs a one-input legacy TestNet P2PKH transaction
// only if the declared prevout address matches the given compressed WIF key.
// It does not validate existence/value of UTXO against the Bitcoin network,
// and never broadcasts data.
func SignLegacyTestnetP2PKH(input UTXO,p Payment,sourceAddress string,wif string)([]byte,error){
 key,err:=DecodeTestnetWIF(wif)
 if err!=nil{return nil,err}
 defer func(){for i:=range key{key[i]=0}}()
 scalar:=new(secp.ModNScalar)
 if overflow:=scalar.SetByteSlice(key);overflow||scalar.IsZero(){
  return nil,errors.New("invalid secp256k1 private scalar")
 }
 priv:=secp.NewPrivateKey(scalar)
 compressed:=priv.PubKey().SerializeCompressed()
 hash,err:=hash160Compressed(compressed)
 if err!=nil{return nil,err}
 match,err:=DecodeTestnetAddress(sourceAddress)
 if err!=nil{return nil,err}
 if !bytes.Equal(hash,match){return nil,errors.New("source address mismatches WIF")}
 script,err:=P2PKHScript(sourceAddress)
 if err!=nil{return nil,err}
 preimage,err:=serializeLegacy(input,p,script)
 if err!=nil{return nil,err}
 // SIGHASH_ALL (legacy): append four bytes 01000000 to serialized preimage.
 var sighash bytes.Buffer
 sighash.Write(preimage);put32(&sighash,1)
 first:=sha256.Sum256(sighash.Bytes())
 second:=sha256.Sum256(first[:])
 der:=ecdsa.Sign(priv,second[:]).Serialize()
 der=append(der,0x01) // SIGHASH_ALL on signature
 if len(der)>=76||len(compressed)>=76 {
  return nil,errors.New("script pushdata unexpectedly large")
 }
 scriptSig:=append([]byte{byte(len(der))},der...)
 scriptSig=append(scriptSig,byte(len(compressed)))
 scriptSig=append(scriptSig,compressed...)
 return serializeLegacy(input,p,scriptSig)
}
