// Package hellocheck implements Bitcoin TestNet address and transaction
// preparation primitives. Drafts are NOT signed or broadcast.
package hellocheck

import (
 "bytes"
 "crypto/sha256"
 "errors"
 "fmt"
 "math/big"
 "strings"
)

const (
 alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
 TestnetP2PKH byte = 0x6f
 MainnetP2PKH byte = 0x00
 TestnetWIF byte = 0xef
)
var errInvalidBase58 = errors.New("invalid base58 character")

func EncodeBase58Check(version byte, payload []byte) string {
 data:=append([]byte{version},payload...)
 x:=sha256.Sum256(data); y:=sha256.Sum256(x[:])
 data=append(data,y[:4]...)
 n:=new(big.Int).SetBytes(data)
 out:=make([]byte,0,len(data)*2)
 quotient:=new(big.Int);rem:=new(big.Int);base:=big.NewInt(58)
 for n.Sign()>0 {
  quotient.QuoRem(n,base,rem)
  out=append(out,alphabet[rem.Int64()])
  n.Set(quotient)
 }
 for _,b:=range data {if b!=0 {break};out=append(out,'1')}
 for i,j:=0,len(out)-1;i<j;i,j=i+1,j-1 {out[i],out[j]=out[j],out[i]}
 return string(out)
}

func DecodeBase58Check(s string)(byte,[]byte,error){
 if s=="" {return 0,nil,errors.New("base58check: empty input")}
 n:=big.NewInt(0)
 for _,r:=range s {
  index:=strings.IndexRune(alphabet,r)
  if index<0{return 0,nil,errInvalidBase58}
  n.Mul(n,big.NewInt(58))
  n.Add(n,big.NewInt(int64(index)))
 }
 leading:=0;for leading<len(s)&&s[leading]=='1' {leading++}
 data:=append(bytes.Repeat([]byte{0},leading),n.Bytes()...)
 if len(data)<5{return 0,nil,errors.New("base58check: too short")}
 content:=data[:len(data)-4]
 one:=sha256.Sum256(content);two:=sha256.Sum256(one[:])
 if !bytes.Equal(two[:4],data[len(data)-4:]) {
  return 0,nil,errors.New("base58check: invalid checksum")
 }
 return content[0],append([]byte(nil),content[1:]...),nil
}

func TestnetAddressFromHash160(payload []byte)(string,error){
 if len(payload)!=20{return "",fmt.Errorf("hash160 must be 20 bytes, got %d",len(payload))}
 return EncodeBase58Check(TestnetP2PKH,payload),nil
}
func DecodeTestnetAddress(address string)([]byte,error){
 version,payload,err:=DecodeBase58Check(address)
 if err!=nil{return nil,err}
 if version!=TestnetP2PKH{return nil,fmt.Errorf("testnet expected version 0x6f; got 0x%02x",version)}
 if len(payload)!=20{return nil,fmt.Errorf("testnet P2PKH requires 20-byte hash, got %d",len(payload))}
 return payload,nil
}
// P2PKHScript is a locking script (scriptPubKey), NOT an input scriptSig.
func P2PKHScript(address string)([]byte,error){
 h,err:=DecodeTestnetAddress(address)
 if err!=nil{return nil,err}
 script:=append([]byte{0x76,0xa9,0x14},h...)
 return append(script,0x88,0xac),nil
}
