from sc_api import ScalableAPI, CLIManager
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)

mgr = CLIManager()
if not mgr.is_installed():
    mgr.download_and_install()

api = ScalableAPI(manager=mgr)

print("\n--- User Installation Code ---")
print(f"Code: {api.get_installation_code()}")

print("Logging in (smart login)...")
broker = api.login(interactive=True)
print(f"Active Session: {broker.user}")

print("\n--- Broker Overview ---")
print(broker.get_overview())

print("\n--- Portfolio Holdings ---")
for item in broker.get_holdings():
    print(item)

print("\n--- Recent Transactions ---")
for item in broker.get_transactions()[:3]:
    print(item)

print("\n--- Security Search (Authenticated) ---")
for security in broker.search("Apple"):
    print(security)