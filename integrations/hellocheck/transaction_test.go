package hellocheck

import (
 "bytes"
 "encoding/binary"
 "encoding/hex"
 "strings"
 "testing"

 secp "github.com/decred/dcrd/dcrec/secp256k1/v4"
 "github.com/decred/dcrd/dcrec/secp256k1/v4/ecdsa"
)

// Wallet material is generated only in process memory. Never print WIF or secret.
func TestTestnetWalletAndCompressedWIF(t *testing.T){
 wallet,err:=NewTestnetWallet()
 if err!=nil{t.Fatal(err)}
 got,err:=DecodeTestnetWIF(wallet.WIF)
 if err!=nil{t.Fatal(err)}
 if len(got)!=32{t.Fatalf("expected 32-byte private key got %d",len(got))}
 if len(wallet.PublicKeyCompressed)!=33{t.Fatal("compressed public key must be 33 bytes")}
 if _,err:=DecodeTestnetAddress(wallet.Address);err!=nil{t.Fatal(err)}
 if _,err:=DecodeTestnetWIF(wallet.Address);err==nil{t.Fatal("address accepted as secret WIF")}
 for i:=range got{got[i]=0}
}
func TestDraftTransactionHasCorrectTxidOrderAndScript(t *testing.T){
 payload:=bytes.Repeat([]byte{0x42},20)
 addr,_:=TestnetAddressFromHash160(payload)
 txid:=strings.Repeat("11",31)+"ff"
 raw,err:=DraftUnsigned(UTXO{TXID:txid,Vout:2,ValueSatoshis:16000},
 Payment{Destination:addr,AmountSatoshis:15000,FeeSatoshis:1000})
 if err!=nil{t.Fatal(err)}
 if len(raw)!=85{t.Fatalf("expected 85 bytes, got %d",len(raw))}
 if !bytes.Equal(raw[:4],[]byte{1,0,0,0}){t.Fatal("wrong version")}
 if raw[4]!=1||raw[5]!=0xff||raw[36]!=0x11{t.Fatal("wrong txid wire endianness")}
 if binary.LittleEndian.Uint32(raw[37:41])!=2 {t.Fatal("wrong vout")}
 if raw[41]!=0 {t.Fatal("unsigned scriptSig was not empty")}
 if !bytes.Equal(raw[42:46],[]byte{255,255,255,255}){t.Fatal("wrong sequence")}
 if raw[46]!=1||binary.LittleEndian.Uint64(raw[47:55])!=15000 {t.Fatal("wrong output value")}
 if raw[55]!=25 {t.Fatal("locking script must be 25 bytes")}
 if raw[56]!=0x76||raw[57]!=0xa9||raw[58]!=0x14||raw[79]!=0x88||raw[80]!=0xac {t.Fatalf("wrong locking script %x",raw[56:81])}
 if binary.LittleEndian.Uint32(raw[81:])!=0 {t.Fatal("wrong locktime")}
}
func TestDraftRejectsInvalidFundsAndDust(t *testing.T){
 addr,_:=TestnetAddressFromHash160(bytes.Repeat([]byte{0x12},20))
 txid:=strings.Repeat("ab",32)
 input:=UTXO{TXID:txid,Vout:1,ValueSatoshis:25000}
 cases:=[]Payment{
 {Destination:addr,AmountSatoshis:26000,FeeSatoshis:1000},
 {Destination:addr,AmountSatoshis:20000,FeeSatoshis:0},
 {Destination:addr,AmountSatoshis:24000,FeeSatoshis:500,ChangeAddress:addr},
 {Destination:addr,AmountSatoshis:22000,FeeSatoshis:1000},
 }
 for _,p:=range cases{
  if _,err:=DraftUnsigned(input,p);err==nil{t.Fatalf("accepted unsafe draft with value/fee/change=%d/%d/%s",p.AmountSatoshis,p.FeeSatoshis,p.ChangeAddress)}
 }
}
func TestSignLegacySighashAllAndWrongOwner(t *testing.T){
 wallet,err:=NewTestnetWallet()
 if err!=nil{t.Fatal(err)}
 otherHash:=bytes.Repeat([]byte{0x5a},20)
 otherAddress,_:=TestnetAddressFromHash160(otherHash)
 input:=UTXO{TXID:strings.Repeat("cc",32),Vout:0,ValueSatoshis:10000}
 p:=Payment{Destination:otherAddress,AmountSatoshis:9500,FeeSatoshis:500}
 if _,err:=SignLegacyTestnetP2PKH(input,p,otherAddress,wallet.WIF);err==nil{
  t.Fatal("signed transaction using unrelated key")}
 raw,err:=SignLegacyTestnetP2PKH(input,p,wallet.Address,wallet.WIF)
 if err!=nil{t.Fatal(err)}
 if len(raw)<150 {t.Fatalf("unexpected signed tx length %d",len(raw))}
 if raw[0]!=1||raw[4]!=1 {t.Fatal("wrong transaction header")}
 scriptLen:=int(raw[41])
 script:=raw[42:42+scriptLen]
 sigPush:=int(script[0])
 if script[sigPush]!=0x01 {t.Fatal("signature missing SIGHASH_ALL byte")}
 pubLen:=int(script[1+sigPush])
 pub:=script[2+sigPush:2+sigPush+pubLen]
 if pubLen!=33{t.Fatal("signed with uncompressed key")}
 signature,err:=ecdsa.ParseDERSignature(script[1:sigPush])
 if err!=nil{t.Fatal(err)}
 origin,err:=secp.ParsePubKey(pub)
 if err!=nil{t.Fatal(err)}
 prevScript,err:=P2PKHScript(wallet.Address)
 if err!=nil{t.Fatal(err)}
 sighashPreimage,err:=serializeLegacy(input,p,prevScript)
 if err!=nil{t.Fatal(err)}
 sighashPreimage=append(sighashPreimage,1,0,0,0)
 hash1:=sha256.Sum256(sighashPreimage);hash2:=sha256.Sum256(hash1[:])
 if !signature.Verify(hash2[:],origin){t.Fatal("secp256k1 signature mismatch")}
 if _,err:=hex.DecodeString(input.TXID);err!=nil{t.Fatal(err)}
}
