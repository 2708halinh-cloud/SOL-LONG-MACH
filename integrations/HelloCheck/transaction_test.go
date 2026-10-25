package hellocheck

import (
    "bytes"
    "encoding/binary"
    "encoding/hex"
    "strings"
    "testing"
)

const (
    sourceAddr = "mujf6HNVrAFUX2gjNgirTWyxaT7XzeKUrj"
    destAddr = "msj42CCGruhRsFrGATiUuh25dtxYtnpbTx"
    sourceTxID = "7756bf4ed3b495adb63e05c02398e799c471b885d10523028b6e1b10f0ae181f"
)
func exampleDraft() Draft {
    return Draft{
        Input: UnsignedInput{TxID:sourceTxID,Vout:1,UTXOSatoshis:25100000},
        Destination: Payment{Address:destAddr,Satoshis:25000000},
        Change:&Payment{Address:sourceAddr,Satoshis:90000},
        FeeSatoshis:10000,
    }
}
func TestDecodedExampleAddressPayloads(t *testing.T) {
    a,err:=DecodeTestnetP2PKH(sourceAddr)
    if err!=nil {t.Fatal(err)}
    if got:=hex.EncodeToString(a[:]);got!="9bf8cee4ce4532eab13454490dbdfb346d5e37f8" {
        t.Fatalf("source pubkeyhash = %s",got)
    }
    b,err:=DecodeTestnetP2PKH(destAddr)
    if err!=nil {t.Fatal(err)}
    if got:=hex.EncodeToString(b[:]);got!="85eb47fe98f349065d6f044e27a4ac541af79ee2" {
        t.Fatalf("destination pubkeyhash = %s",got)
    }
}
func TestRejectCorruptOrWrongNetworkAddress(t *testing.T) {
    candidates:=[]string{"",sourceAddr[:len(sourceAddr)-1]+"1","0test", 
        "1BoatSLRHtKNngkdXEeobR76b53LETtpyT"}
    for _,c:=range candidates {
        if _,err:=DecodeTestnetP2PKH(c);err==nil {t.Fatalf("accepted %q",c)}
    }
}
func TestSerializedTemplateIsUnsignedAndCorrectEndian(t *testing.T) {
    b,err:=BuildUnsignedTestnetP2PKH(exampleDraft())
    if err!=nil {t.Fatal(err)}
    if len(b)!=119 { t.Fatalf("unexpected serialized length %d",len(b)) }
    if !bytes.Equal(b[:5],[]byte{1,0,0,0,1}) {t.Fatal("version/input count mismatch")}
    source,_:=hex.DecodeString(sourceTxID)
    for i:=0;i<32;i++ {if b[5+i]!=source[31-i] {t.Fatal("txid not little-endian")}}
    if binary.LittleEndian.Uint32(b[37:41])!=1 {t.Fatal("incorrect output index")}
    if b[41]!=0 {t.Fatal("scriptSig must be empty until signing")}
    if !bytes.Equal(b[42:46],[]byte{0xff,0xff,0xff,0xff}) {t.Fatal("sequence mismatch")}
    if b[46]!=2 {t.Fatal("missing change output")}
    if binary.LittleEndian.Uint64(b[47:55])!=25000000 {t.Fatal("satoshi LE mismatch")}
    if b[55]!=25 || !bytes.Equal(b[56:59],[]byte{0x76,0xa9,0x14}) {
        t.Fatal("not a P2PKH scriptPubKey")
    }
    if binary.LittleEndian.Uint64(b[81:89])!=90000 {t.Fatal("incorrect change amount")}
    if !bytes.Equal(b[len(b)-4:],[]byte{0,0,0,0}) {t.Fatal("nonzero locktime")}
}
func TestRefuseImplicitExcessiveFee(t *testing.T) {
    d:=exampleDraft();d.Change=nil
    if _,err:=BuildUnsignedTestnetP2PKH(d);err==nil {t.Fatal("implicit fee accepted")}
}
func TestRejectMismatchedChange(t *testing.T) {
    d:=exampleDraft();d.Change.Satoshis=100
    if _,err:=BuildUnsignedTestnetP2PKH(d);err==nil {t.Fatal("wrong change accepted")}
}
func TestAllowNoChangeOnlyIfExact(t *testing.T) {
    d:=exampleDraft();d.Input.UTXOSatoshis=25010000;d.Change=nil
    if b,err:=BuildUnsignedTestnetP2PKH(d);err!=nil || len(b)==0 {
        t.Fatalf("exact fee case failed: %v",err)
    }
}
func TestRejectMalformedTxidAndUTXO(t *testing.T) {
    d:=exampleDraft();d.Input.TxID="1234"
    if _,err:=BuildUnsignedTestnetP2PKH(d);err==nil {t.Fatal("short txid accepted")}
    d=exampleDraft();d.Input.UTXOSatoshis=10
    if _,err:=BuildUnsignedTestnetP2PKH(d);err==nil {t.Fatal("overspend accepted")}
    d=exampleDraft();d.Destination.Address=strings.Repeat("x",10)
    if _,err:=BuildUnsignedTestnetP2PKH(d);err==nil {t.Fatal("invalid destination accepted")}
}
