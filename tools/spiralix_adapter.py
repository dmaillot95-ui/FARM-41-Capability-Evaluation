#!/usr/bin/env python3
"""CEREBRON Ω — SPIRALIX farm adapter v0.1. Deterministic transport; no evidence upgrade."""
import json,hashlib
R=("farm_id","domain","objective","method","evidence_level","validation","priority","task_type"); E={f"E{i}" for i in range(9)}
def encode(**k):
 m=[x for x in R if x not in k]
 if m: raise ValueError("missing:"+",".join(m))
 if k["evidence_level"] not in E: raise ValueError("invalid evidence_level")
 x={"language":"SPIRALIX-OMEGA","layer":"GLYPH-VECTOR-OMEGA","vector":{q:k[q] for q in R},"payload":k.get("payload",{})}; raw=json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False); x["sha256"]=hashlib.sha256(raw.encode()).hexdigest(); return x
def verify(x):
 y=dict(x);c=y.pop("sha256",None);return c==hashlib.sha256(json.dumps(y,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def decode(x):
 if not verify(x):raise ValueError("HASH_MISMATCH")
 return x["vector"],x.get("payload",{})
if __name__=="__main__":
 import argparse;p=argparse.ArgumentParser();p.add_argument("--farm",required=True);p.add_argument("--domain",required=True);a=p.parse_args();x=encode(farm_id=a.farm,domain=a.domain,objective="interop-self-test",method="deterministic-roundtrip",evidence_level="E2",validation="VERIFY",priority="normal",task_type="interop",payload={"claim":"transport test only"});v,p=decode(x);assert v["farm_id"]==a.farm and p["claim"]=="transport test only";print(json.dumps({"status":"VERIFIED","farm_id":a.farm,"sha256":x["sha256"]}))
