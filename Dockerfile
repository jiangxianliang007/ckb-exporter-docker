FROM python:3.9

WORKDIR /config
COPY ./ckb_exporter_agent.py ./requirements.txt /config/
RUN pip3 install -r requirements.txt
ENV PORT=3000

CMD "python3" "ckb_exporter_agent.py" "$ckb_rpc" "$ckb_indexer_rpc"
