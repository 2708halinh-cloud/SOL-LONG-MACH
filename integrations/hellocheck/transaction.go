package hellocheck

import (
 "bytes"
 "encoding/binary"
 "encoding/hex"
 "errors"
 "fmt"
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
