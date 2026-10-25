package hellocheck

import (
 "bytes"
 "context"
 "encoding/hex"
 "encoding/json"
 "errors"
 "fmt"
 "io"
 "net"
 "net/http"
 "net/url"
 "strings"
 "time"
)

// RPCAuth stays in memory only; callers must pass trusted Bitcoin Core
// credentials from their execution environment, never from repository files.
type RPCAuth struct{ User, Password string }
type rpcReply struct{
 Result json.RawMessage `json:"result"`
 Error *struct{Code int `json:"code"`;Message string `json:"message"`} `json:"error"`
}

func testnetNodeURL(raw string)(string,error){
 u,err:=url.Parse(raw)
 if err!=nil||u==nil||u.Hostname()==""||u.User!=nil||u.Fragment!=""{
  return "",errors.New("invalid Bitcoin RPC endpoint")
 }
 if u.Scheme!="https" {
  if u.Scheme!="http"{return "",errors.New("unsupported RPC URL scheme")}
  host:=u.Hostname()
  ip:=net.ParseIP(host)
  if !strings.EqualFold(host,"localhost") && (ip==nil||!ip.IsLoopback()){
   return "",errors.New("plaintext Bitcoin RPC only allowed on loopback")
  }
 }
 return u.String(),nil
}
func rpcCall(ctx context.Context, client *http.Client, endpoint string, auth RPCAuth, method string, params []any)(json.RawMessage,error){
 reqBody,err:=json.Marshal(map[string]any{
  "jsonrpc":"1.0","id":"hellocheck-testnet","method":method,"params":params,
 })
 if err!=nil{return nil,err}
 req,err:=http.NewRequestWithContext(ctx,http.MethodPost,endpoint,bytes.NewReader(reqBody))
 if err!=nil{return nil,err}
 req.SetBasicAuth(auth.User,auth.Password)
 req.Header.Set("Content-Type","application/json")
 resp,err:=client.Do(req)
 if err!=nil{return nil,err}
 defer resp.Body.Close()
 raw,err:=io.ReadAll(io.LimitReader(resp.Body,1<<20))
 if err!=nil{return nil,err}
 // A JSON-RPC failure may use status 500. Do not echo HTTP body which
 // could contain provider debug output, credentials, or private account data.
 var reply rpcReply
 if err:=json.Unmarshal(raw,&reply);err!=nil{
  return nil,errors.New("Bitcoin RPC returned invalid JSON")
 }
 if reply.Error!=nil{
  return nil,fmt.Errorf("Bitcoin RPC method %s rejected with code %d",method,reply.Error.Code)
 }
 if resp.StatusCode!=http.StatusOK{
  return nil,fmt.Errorf("Bitcoin RPC %s returned HTTP %d",method,resp.StatusCode)
 }
 return reply.Result,nil
}

// BroadcastTestnet posts an already-signed raw transaction ONLY on an
// explicit caller request to an authenticated Bitcoin Core TestNet RPC node.
// It checks node chain before ever calling sendrawtransaction.
func BroadcastTestnet(ctx context.Context, endpoint string, auth RPCAuth, signedHex string)(string,error){
 node,err:=testnetNodeURL(endpoint)
 if err!=nil{return "",err}
 if strings.TrimSpace(auth.User)==""||strings.TrimSpace(auth.Password)==""{
  return "",errors.New("Bitcoin RPC credentials are required")
 }
 raw,err:=hex.DecodeString(strings.TrimSpace(signedHex))
 if err!=nil||len(raw)<85{return "",errors.New("signed transaction hex is invalid")}
 if len(raw)<43||raw[4]!=1||raw[41]==0||raw[41]>=0xfd {
  return "",errors.New("only signed one-input legacy P2PKH transactions can be broadcast")
 }
 client:=&http.Client{
  Timeout:12*time.Second,
  CheckRedirect:func(_ *http.Request,_ []*http.Request)error{
   return http.ErrUseLastResponse
  },
 }
 info,err:=rpcCall(ctx,client,node,auth,"getblockchaininfo",[]any{})
 if err!=nil{return "",err}
 var chain struct{Chain string `json:"chain"`}
 if err:=json.Unmarshal(info,&chain);err!=nil{return "",errors.New("chain identification failed")}
 if chain.Chain!="test"&&chain.Chain!="testnet4" {
  return "",errors.New("node is not Bitcoin TestNet; broadcast refused")
 }
 result,err:=rpcCall(ctx,client,node,auth,"sendrawtransaction",[]any{strings.TrimSpace(signedHex)})
 if err!=nil{return "",err}
 var txid string
 if err:=json.Unmarshal(result,&txid);err!=nil{return "",errors.New("invalid node transaction ID")}
 decoded,err:=hex.DecodeString(txid)
 if err!=nil||len(decoded)!=32{return "",errors.New("node returned invalid transaction ID")}
 return txid,nil
}
