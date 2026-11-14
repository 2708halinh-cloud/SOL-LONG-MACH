package hellocheck

import (
 "crypto/sha256"
 "errors"

 secp "github.com/decred/dcrd/dcrec/secp256k1/v4"
 "golang.org/x/crypto/ripemd160"
)
type Wallet struct {
 Address string
 WIF string // SECRET: never print, log, persist or send without separate deliberate action.
 PublicKeyCompressed []byte
}
func NewTestnetWallet()(Wallet,error){
 // secp256k1.GeneratePrivateKey reads cryptographically secure entropy.
 privateKey,err:=secp.GeneratePrivateKey()
 if err!=nil {return Wallet{},err}
 secret:=privateKey.Serialize()
 defer func(){for i:=range secret{secret[i]=0}}()
 compressed:=privateKey.PubKey().SerializeCompressed()
 h:=sha256.Sum256(compressed)
 ripemd:=ripemd160.New()
 if _,err:=ripemd.Write(h[:]);err!=nil{return Wallet{},err}
 address,err:=TestnetAddressFromHash160(ripemd.Sum(nil))
 if err!=nil{return Wallet{},err}
 payload:=append(append([]byte{},secret...),0x01) // compressed WIF
 wif:=EncodeBase58Check(TestnetWIF,payload)
 return Wallet{Address:address,WIF:wif,PublicKeyCompressed:compressed},nil
}
func DecodeTestnetWIF(wif string)([]byte,error){
 ver,payload,err:=DecodeBase58Check(wif)
 if err!=nil{return nil,err}
 if ver!=TestnetWIF||len(payload)!=33||payload[32]!=0x01{
  return nil,errors.New("expected compressed Bitcoin TestNet WIF")
 }
 return append([]byte(nil),payload[:32]...),nil
}
