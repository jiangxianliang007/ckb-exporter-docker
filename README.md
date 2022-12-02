# ckb-exporter-docker

run in docker
```
docker run -d -it -p 3000:3000 -e ckb_rpc=http://testnet.ckb.dev -e ckb_indexer_rpc=http://testnet.ckb.dev/indexer jiangxianliang/ckbindexer-exporter:0.2

curl http://127.0.0.1:3000/metrics/ckb
```
