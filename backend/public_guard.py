"""Persistent admission and conservative cost reservations for a small public demo."""
import hmac
import math
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from backend import config

class GuardError(RuntimeError):
    def __init__(self,message,status=429):
        super().__init__(message);self.status=status

class PublicGuard:
    def __init__(self,path,code,max_analyses,budget,input_rate,output_rate):
        if not code or max_analyses < 1 or not all(math.isfinite(n) and n > 0 for n in (budget, input_rate, output_rate)):
            raise ValueError("Public mode requires an access code, analysis limit, budget and verified model prices.")
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        self.code=code;self.max_analyses=max_analyses
        self.budget=math.floor(budget*1_000_000)
        self.input_rate=input_rate;self.output_rate=output_rate
        with self._connect() as db:
            db.execute('CREATE TABLE IF NOT EXISTS admissions (created REAL NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS reservations (micro_usd INTEGER NOT NULL)')
    @contextmanager
    def _connect(self):
        db = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        try:
            with db:
                yield db
        finally:
            db.close()
    def admit(self,code):
        if not hmac.compare_digest(code.encode(),self.code.encode()):
            raise GuardError("Enter the judge access code to run an inspection.",401)
        with self._connect() as db:
            db.execute('BEGIN IMMEDIATE')
            total=db.execute('SELECT count(*) FROM admissions').fetchone()[0]
            recent=db.execute('SELECT count(*) FROM admissions WHERE created > ?',(time.time()-60,)).fetchone()[0]
            if total >= self.max_analyses: raise GuardError("This demo has reached its inspection limit.")
            if recent >= 2: raise GuardError("The demo is busy. Please wait a minute before trying again.")
            db.execute('INSERT INTO admissions VALUES (?)',(time.time(),));db.commit()
    def reserve(self,input_tokens,max_output_tokens):
        if input_tokens > config.MAX_INPUT_TOKENS:
            raise GuardError("This image produces too much analysis context. Try a simpler crop image.",413)
        # Reserve full output capacity plus a buffer on the provider's input estimate.
        amount=math.ceil((input_tokens*1.2+512)*self.input_rate+max_output_tokens*self.output_rate)
        with self._connect() as db:
            db.execute('BEGIN IMMEDIATE')
            spent=db.execute('SELECT coalesce(sum(micro_usd),0) FROM reservations').fetchone()[0]
            if spent+amount > self.budget:raise GuardError("The public demo's analysis budget is exhausted.")
            db.execute('INSERT INTO reservations VALUES (?)',(amount,));db.commit()
        return amount

_guard=None
def get_public_guard():
    global _guard
    if not config.PUBLIC_MODE:return None
    if not config.ANTHROPIC_API_KEY or config.VIRGO_DEMO_MODE:
        raise ValueError("Public mode requires a live Anthropic connection.")
    if _guard is None:
        _guard=PublicGuard(config.USAGE_DB,config.ACCESS_CODE,config.MAX_ANALYSES,
            config.DEMO_BUDGET_USD,config.INPUT_USD_PER_M,config.OUTPUT_USD_PER_M)
    return _guard
