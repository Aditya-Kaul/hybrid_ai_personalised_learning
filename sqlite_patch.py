# sqlite_patch.py
import sys
import pysqlite3

sys.modules['sqlite3'] = pysqlite3