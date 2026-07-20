import sqlite3

conn = sqlite3.connect("analytics.db")
cursor = conn.cursor()
cursor.execute("UPDATE config SET value='nvidia' WHERE key='llm_provider'")
cursor.execute("UPDATE config SET value='meta/llama-3.1-70b-instruct' WHERE key='llm_model'")
conn.commit()
conn.close()
print("Reset configuration successfully to NVIDIA + Llama 3.1 70B.")
