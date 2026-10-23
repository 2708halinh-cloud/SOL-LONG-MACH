package hellocheck

import (
 "context"
 "encoding/hex"
 "encoding/json"
 "net/http"
 "net/http/httptest"
 "strings"
 "sync/atomic"
 "testing"
)

func testSignedHex(t *testing.T)string{
 t.Helper()
 wallet,err:=NewTestnetWallet()
 if err!=nil{t.Fatal(err)}
 raw,err:=SignLegacyTestnetP2PKH(
  UTXO{TXID:strings.Repeat("ab",32),Vout:0,ValueSatoshis:100000},
  Payment{Destination:wallet.Address,AmountSatoshis:99000,FeeSatoshis:1000},
  wallet.Address,wallet.WIF)
 if err!=nil{t.Fatal(err)}
 return hex.EncodeToString(raw)
}
func fakeBitcoinRPC(t *testing.T, chain string, sendCalls *atomic.Int32)*httptest.Server{
 t.Helper()
 return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter,r *http.Request){
  user,pass,ok:=r.BasicAuth()
  if !ok||user!="testuser"||pass!="testpassword"{t.Error("missing authenticated RPC request");w.WriteHeader(401);return}
  if r.Method!=http.MethodPost{t.Error("expected POST")}
  var request struct{
   Method string `json:"method"`
   Params []json.RawMessage `json:"params"`
  }
  if err:=json.NewDecoder(r.Body).Decode(&request);err!=nil{t.Error(err);return}
  w.Header().Set("Content-Type","application/json")
  if request.Method=="getblockchaininfo"{
   _=json.NewEncoder(w).Encode(map[string]any{
    "result":map[string]string{"chain":chain},"error":nil,"id":"hellocheck-testnet",
   })
  } else if request.Method=="sendrawtransaction" {
   sendCalls.Add(1)
   if len(request.Params)!=1{t.Error("expected one raw tx")}
   _=json.NewEncoder(w).Encode(map[string]any{
    "result":strings.Repeat("a5",32),"error":nil,"id":"hellocheck-testnet",
   })
  } else {t.Errorf("unexpected Bitcoin RPC method %q",request.Method)}
 }))
}

func TestBroadcastOnlyTestnetNodeAndExplicitAuthentication(t *testing.T){
 var count atomic.Int32
 srv:=fakeBitcoinRPC(t,"test",&count)
 defer srv.Close()
 got,err:=BroadcastTestnet(context.Background(),srv.URL,
  RPCAuth{User:"testuser",Password:"testpassword"},testSignedHex(t))
 if err!=nil{t.Fatal(err)}
 if got!=strings.Repeat("a5",32){t.Fatalf("wrong transaction id %q",got)}
 if count.Load()!=1{t.Fatalf("expected one TestNet sendrawtransaction call, got %d",count.Load())}
}

func TestRejectMainnetWithoutSending(t *testing.T){
 var count atomic.Int32
 srv:=fakeBitcoinRPC(t,"main",&count)
 defer srv.Close()
 if _,err:=BroadcastTestnet(context.Background(),srv.URL,
  RPCAuth{User:"testuser",Password:"testpassword"},testSignedHex(t));err==nil{
  t.Fatal("broadcast to mainnet was not denied")
 }
 if count.Load()!=0{t.Fatalf("mainnet broadcast attempted: %d",count.Load())}
}

func TestRejectPlaintextRemoteAndMissingCredentials(t *testing.T){
 if _,err:=BroadcastTestnet(context.Background(),"http://example.com:18332",
 RPCAuth{User:"testuser",Password:"testpassword"},strings.Repeat("ab",90));err==nil{
  t.Fatal("plaintext non-loopback RPC permitted")
 }
 if _,err:=BroadcastTestnet(context.Background(),"http://127.0.0.1:18332",
 RPCAuth{},strings.Repeat("ab",90));err==nil{t.Fatal("anonymous RPC permitted")}
}

func TestRejectUnsignedTransactionWithoutRPC(t *testing.T){
 var count atomic.Int32
 srv:=fakeBitcoinRPC(t,"test",&count)
 defer srv.Close()
 wallet,err:=NewTestnetWallet()
 if err!=nil{t.Fatal(err)}
 raw,err:=DraftUnsigned(UTXO{TXID:strings.Repeat("aa",32),ValueSatoshis:10000},
 Payment{Destination:wallet.Address,AmountSatoshis:9000,FeeSatoshis:1000})
 if err!=nil{t.Fatal(err)}
 if _,err:=BroadcastTestnet(context.Background(),srv.URL,
 RPCAuth{User:"testuser",Password:"testpassword"},hex.EncodeToString(raw));err==nil{
  t.Fatal("broadcast permitted for unsigned transaction")
 }
 if count.Load()!=0{t.Fatal("network send called on unsigned transaction")}
}
