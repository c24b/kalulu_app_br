from .config import cfg
import importlib

ENV = "local"

cfg = cfg.get(ENV)
print(cfg["SRV_NAME"])
