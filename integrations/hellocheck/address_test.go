package hellocheck

import (
 "bytes"
 "encoding/hex"
 "strings"
 "testing"
)

func TestBase58RoundtripAndNetwork(t *testing.T) {
 payload:=make([]byte,20)
 payload[19]=0x42
 addr,err:=TestnetAddressFromHash160(payload)
 if err!=nil{t.Fatal(err)}
 if addr[0]!='m' && addr[0]!='n' {t.Fatalf("unexpected TestNet prefix: %s",addr)}
 got,err:=DecodeTestnetAddress(addr)
 if err!=nil{t.Fatal(err)}
 if !bytes.Equal(got,payload){t.Fatalf("wrong decoded payload: %x",got)}
 ver,p,err:=DecodeBase58Check(addr)
 if err!=nil||ver!=TestnetP2PKH||!bytes.Equal(p,payload){t.Fatal("base58check roundtrip mismatch")}
 s:=EncodeBase58Check(MainnetP2PKH,payload)
 if _,err:=DecodeTestnetAddress(s);err==nil{t.Fatal("mainnet address accepted as testnet")}
 if _,err:=DecodeTestnetAddress(addr[:len(addr)-1]+"0");err==nil{t.Fatal("invalid alphabet character accepted")}
}

func TestChecksumAndScript(t *testing.T) {
 payload,_:=hex.DecodeString(strings.Repeat("1e",20))
 addr,_:=TestnetAddressFromHash160(payload)
 altered:="1"+addr[1:]
 if _,_,err:=DecodeBase58Check(altered);err==nil{t.Fatal("invalid checksum accepted")}
 script,err:=P2PKHScript(addr)
 if err!=nil{t.Fatal(err)}
 if len(script)!=25||script[0]!=0x76||script[1]!=0xa9||script[2]!=0x14||script[23]!=0x88||script[24]!=0xac {
  t.Fatalf("unexpected P2PKH script %x",script)
 }
 if !bytes.Equal(script[3:23],payload){t.Fatal("hash160 mismatch")}
}

func TestRejectInvalidHash160(t *testing.T) {
 if _,err:=TestnetAddressFromHash160(make([]byte,19));err==nil{t.Fatal("accepted 19-byte hash160")}
}
