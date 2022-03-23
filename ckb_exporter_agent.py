#encoding: utf-8

import requests
import prometheus_client
from prometheus_client import Gauge
from prometheus_client.core import CollectorRegistry
from flask import Response, Flask, request, current_app
import os
import sys


CKB_RPC = sys.argv[1]
CKB_INDEXER_RPC = sys.argv[2]

NodeFlask = Flask(__name__)

def convert_int(value):
    try:
        return int(value)
    except ValueError:
        return int(value, base=16)
    except Exception as exp:
        raise exp

class RpcGet(object):
    def __init__(self, CKB_RPC, CKB_INDEXER_RPC):
        self.CKB_RPC = CKB_RPC
        self.CKB_INDEXER_RPC = CKB_INDEXER_RPC
    def get_ckb_Info(self):
        headers = {"Content-Type":"application/json"}
        data = '{"id":2, "jsonrpc":"2.0", "method":"tx_pool_info", "params":[]}'
        try:
            r = requests.post(
                url="%s" %(self.CKB_RPC),
                data=data,
                headers=headers
            )
            replay = r.json()["result"]
            return {
                "last_blocknumber": convert_int(replay["tip_number"]),
                "total_tx_cycles": convert_int(replay["total_tx_cycles"]),
                "total_tx_size": convert_int(replay["total_tx_size"]),
                "last_block_hash": str(replay["tip_hash"]),
                "last_block_timestamp": convert_int(replay["last_txs_updated_at"])
            }
        except:
            return {
                "last_blocknumber": "-1",
                "total_tx_cycles": "-1",
                "total_tx_size": "-1",
                "last_block_hash": "-1",
                "last_block_timestamp": "-1"
            }

    def get_ckb_indexer_Info(self):
        headers = {"Content-Type":"application/json"}
        data = '{"id":2, "jsonrpc":"2.0", "method":"get_tip", "params":[]}'
        try:
            r = requests.post(
                url="%s" %(self.CKB_INDEXER_RPC),
                data=data,
                headers=headers
            )
            replay = r.json()["result"]
            return {
                "last_blocknumber": convert_int(replay["block_number"]),
                "last_block_hash": str(replay["block_hash"]),
            }
        except:
            return {
                "last_blocknumber": "-1",
                "last_block_hash": "-1",
            }

@NodeFlask.route("/metrics/ckb")
def rpc_get():
    CKB_Chain = CollectorRegistry(auto_describe=False)
    Get_CKB_Info = Gauge("Get_LastBlockInfo",
                                   "Get LastBlockInfo, label include last_block_hash, last_blocknumber, total_tx_cycles, total_tx_size. value is last_block_timestamp;",
                                   ["last_block_hash", "last_block_number", "last_block_tx_cycles", "last_block_tx_size", "last_block_timestamp"],
                                   registry=CKB_Chain)
    Get_CKB_TX_Pool = Gauge("Get_CKBtotal_tx_size",
                                   "Get_CKBtotal_tx_size, Current trading pool usage size",
                                   ["ckb_total_tx_size"],
                                   registry=CKB_Chain)
    Get_CKB_Indexer_Info = Gauge("Get_indexerLastBlockInfo",
                                   "Get LastBlockInfo, label include last_block_hash, last_blocknumber. value is last_block_timestamp;",
                                   ["last_block_hash", "last_block_number"],
                                   registry=CKB_Chain)

    get_result = RpcGet(CKB_RPC,CKB_INDEXER_RPC)
    ckb_last_block_info = get_result.get_ckb_Info()
    Get_CKB_Info.labels(
        last_block_hash=ckb_last_block_info["last_block_hash"],
        last_block_number=ckb_last_block_info["last_blocknumber"],
        last_block_tx_cycles=ckb_last_block_info["total_tx_cycles"],
        last_block_tx_size=ckb_last_block_info["total_tx_size"],
        last_block_timestamp=ckb_last_block_info["last_block_timestamp"]
    ).set(ckb_last_block_info["last_blocknumber"])
    
    Get_CKB_TX_Pool.labels(
        ckb_total_tx_size=ckb_last_block_info["total_tx_size"]
    ).set(ckb_last_block_info["total_tx_size"]) 
 
    indexer_last_block_info = get_result.get_ckb_indexer_Info()
    Get_CKB_Indexer_Info.labels(
        last_block_hash=indexer_last_block_info["last_block_hash"],
        last_block_number=indexer_last_block_info["last_blocknumber"],
    ).set(indexer_last_block_info["last_blocknumber"])
    return Response(prometheus_client.generate_latest(CKB_Chain), mimetype="text/plain")

if __name__ == "__main__":
    NodeFlask.run(host="0.0.0.0",port=3000)
