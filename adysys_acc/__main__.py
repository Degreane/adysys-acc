import adysys_acc as acc
import adysys_acc.cfg as cfg
import subprocess
import os

if __name__ == '__main__':
    server = acc.adyServer(cfg=cfg.cfg)
    cwd = os.getcwd()

else:
    print("Running Imported ")
