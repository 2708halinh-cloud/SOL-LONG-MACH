// Command hellocheck is a standalone, local-only Bitcoin TestNet wallet tool.
// By default it never contacts any blockchain node and never prints private keys.
package main
import (
 "encoding/hex"
 "encoding/json"
 "errors"
 "flag"
 "fmt"
 "os"
 "path/filepath"
 "strings"

 hc "github.com/2708halinh-cloud/SOL-LONG-MACH/integrations/hellocheck"
)
type walletFile struct{
 Format string `json:"format"`
 Network string `json:"network"`
 Address string `json:"address"`
 WIF string `json:"wif"`
}
func fail(err error){fmt.Fprintln(os.Stderr,"HelloCheck:",err);os.Exit(2)}
func usage(){fmt.Fprintln(os.Stderr,"usage: hellocheck create --wallet /private/path.json | address --hash160 HEX | inspect --address ADDRESS | unsigned --txid TXID --vout N --input-sats N --dest ADDRESS --sats N --fee N [--change ADDRESS] | sign --wallet /private/path.json --txid TXID --vout N --input-sats N --dest ADDRESS --sats N --fee N [--change ADDRESS]");os.Exit(2)}
func openWallet(path string)(walletFile,error){
 if path==""{return walletFile{},errors.New("wallet path is required")}
 info,err:=os.Stat(path)
 if err!=nil{return walletFile{},err}
 if info.Mode()&0077!=0 {return walletFile{},errors.New("wallet permissions too broad; require 0600")}
 raw,err:=os.ReadFile(path)
 if err!=nil{return walletFile{},err}
 var w walletFile
 if err:=json.Unmarshal(raw,&w);err!=nil{return w,err}
 if w.Network!="testnet"||w.Format!="HELLOCHECK_TESTNET_LEGACY_V1"{
  return w,errors.New("invalid wallet format or non-TestNet wallet")}
 if _,err:=hc.DecodeTestnetAddress(w.Address);err!=nil{return w,err}
 if _,err:=hc.DecodeTestnetWIF(w.WIF);err!=nil{return w,err}
 return w,nil
}
func main(){
 if len(os.Args)<2{usage()}
 switch os.Args[1]{
 case "create":
  f:=flag.NewFlagSet("create",flag.ExitOnError)
  target:=f.String("wallet","","private output wallet JSON path, will never overwrite")
  _=f.Parse(os.Args[2:])
  if *target==""{fail(errors.New("--wallet required"))}
  wallet,err:=hc.NewTestnetWallet();if err!=nil{fail(err)}
  out:=walletFile{Format:"HELLOCHECK_TESTNET_LEGACY_V1",Network:"testnet",Address:wallet.Address,WIF:wallet.WIF}
  raw,err:=json.MarshalIndent(out,"","  ");if err!=nil{fail(err)}
  fd,err:=os.OpenFile(*target,os.O_WRONLY|os.O_CREATE|os.O_EXCL,0600)
  if err!=nil{fail(err)}
  if _,err=fd.Write(append(raw,'\n'));err!=nil{fd.Close();fail(err)}
  if err=fd.Sync();err!=nil{fd.Close();fail(err)}
  if err=fd.Close();err!=nil{fail(err)}
  fmt.Println("TESTNET_ADDRESS",wallet.Address)
  fmt.Println("WALLET_SAVED_LOCALLY",filepath.Clean(*target))
  fmt.Println("WIF_NOT_PRINTED_OR_UPLOADED")
 case "address":
  f:=flag.NewFlagSet("address",flag.ExitOnError)
  h:=f.String("hash160","","20-byte hash encoded as hex")
  _=f.Parse(os.Args[2:])
  raw,err:=hex.DecodeString(*h);if err!=nil{fail(err)}
  addr,err:=hc.TestnetAddressFromHash160(raw);if err!=nil{fail(err)}
  fmt.Println(addr)
 case "inspect":
  f:=flag.NewFlagSet("inspect",flag.ExitOnError)
  addr:=f.String("address","","TestNet P2PKH address")
  _=f.Parse(os.Args[2:])
  payload,err:=hc.DecodeTestnetAddress(*addr);if err!=nil{fail(err)}
  fmt.Println(hex.EncodeToString(payload))
 case "unsigned","sign":
  f:=flag.NewFlagSet(os.Args[1],flag.ExitOnError)
  walletPath:=f.String("wallet","","private local wallet file (sign only)")
  txid:=f.String("txid","","funded previous TestNet txid; not verified by this CLI")
  vout:=f.Uint("vout",0,"previous output index")
  inputSats:=f.Uint64("input-sats",0,"verified input value in satoshis")
  dest:=f.String("dest","","TestNet P2PKH recipient")
  amount:=f.Uint64("sats",0,"recipient amount in satoshis")
  fee:=f.Uint64("fee",0,"miner fee in satoshis")
  change:=f.String("change","","explicit TestNet change address")
  _=f.Parse(os.Args[2:])
  if *vout>0xffffffff {fail(errors.New("vout out of range"))}
  input:=hc.UTXO{TXID:*txid,Vout:uint32(*vout),ValueSatoshis:*inputSats}
  p:=hc.Payment{Destination:*dest,AmountSatoshis:*amount,FeeSatoshis:*fee,ChangeAddress:*change}
  var raw []byte;var err error
  if os.Args[1]=="sign"{
   w,readErr:=openWallet(*walletPath);if readErr!=nil{fail(readErr)}
   if *change!=""&&strings.TrimSpace(*change)==""{fail(errors.New("invalid change address"))}
   raw,err=hc.SignLegacyTestnetP2PKH(input,p,w.Address,w.WIF)
   if err!=nil{fail(err)}
   fmt.Println("SIGNED_TESTNET_TRANSACTION_NOT_BROADCAST")
  }else{
   raw,err=hc.DraftUnsigned(input,p);if err!=nil{fail(err)}
   fmt.Println("UNSIGNED_TRANSACTION_NOT_BROADCASTABLE")
  }
  fmt.Println(hex.EncodeToString(raw))
 default:usage()
 }
}
