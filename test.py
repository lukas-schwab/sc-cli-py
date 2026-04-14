from sc_api import ScalableAPI, CLIManager
import logging

logging.basicConfig(level=logging.INFO)

api = ScalableAPI()

broker = api.login(interactive=False)

df = broker.get_holdings().to_df()
print(df)