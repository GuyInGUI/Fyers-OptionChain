from fyers_apiv3 import fyersModel
from utils import load_access_token
from dotenv import load_dotenv
load_dotenv()
import re
import os

client_id = os.getenv('CLIENT_ID')

class OptionsChain:
    def __init__(self,symbol) -> None:
        self.access_token = load_access_token()
        self.fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=self.access_token, log_path="")
        self.symbol = symbol
        self.option_chain = self.get_option_chain()
        pass

    def get_expiry_day(self, strike_count=20):
        data = {
            "symbol": self.symbol,
            "strikecount": strike_count,
            "timestamp": ""
        }
        response = self.fyers.optionchain(data=data)
        expiry_day = response['data']['expiryData'][0]['date']
        return expiry_day

    def get_option_chain(self, strike_count=30):
        data = {
            "symbol": self.symbol,
            "strikecount": strike_count,
            "timestamp": ""
        }
        
        response = self.fyers .optionchain(data=data)
        options_chain = response['data']['optionsChain']
        return options_chain

    def find_closest_option(self, target_ltp, option_type):
        closest_ltp = float('inf')
        closest_option = None

        for option in self.option_chain:
            if 'ltp' in option and (option_type is None or option.get('option_type') == option_type):
                diff = abs(option['ltp'] - target_ltp)
                
                if diff < abs(closest_ltp - target_ltp):
                    closest_ltp = option['ltp']
                    closest_option = option

        if closest_option:
            DIFFERENCE = 30 #Load and set this environment variable
            if closest_ltp > target_ltp+DIFFERENCE:
                # If the LTP is greater than 30, get the lower strike
                lower_strike_string = self.get_lower_strike(closest_option.get('symbol', ''))
                if lower_strike_string:
                    # Find the option with the lower strike
                    lower_strike_option = self.find_option_by_symbol(lower_strike_string)
                    if lower_strike_option:
                        closest_option = lower_strike_option
                        closest_ltp = lower_strike_option.get('ltp', 'N/A')
                    else:
                        print(f"No option found for the lower strike: {lower_strike_string}")
                        return None

            print(f"Option with LTP closest to {target_ltp}:")
            print(f"LTP: {closest_ltp}")
            print(f"Strike Price: {closest_option.get('strike_price', 'N/A')}")
            print(f"Option Type: {closest_option.get('option_type', 'N/A')}")
            print(f"Symbol: {closest_option.get('symbol', 'N/A')}")
        else:
            print(f"No {'options' if option_type is None else option_type + ' options'} found in the chain.")

        return closest_option
    
    def get_lower_strike(self, stike):
        strike = stike
        # Input string

        # Split the string by ':' to isolate the part after 'NSE:'
        parts = strike.split(':')[1]

        # Extract the instrument name, strike price, and option type
        instrument = parts[:-7]  # Everything except the last 7 characters
        strike_price = parts[-7:-2]  # The 5-digit number in the middle
        option_type = parts[-2:]  # The last 2 characters
        if "BANKNIFTY" in instrument:
            lower_strike = int(strike_price) - 100
            lower_strike_string = f"{instrument}{lower_strike}{option_type}"
        elif "NIFTY" in instrument:
            lower_strike = int(strike_price) - 50
            lower_strike_string = f"{instrument}{lower_strike}{option_type}"
        elif "SENSEX" in instrument:
            lower_strike = int(strike_price) - 100
            lower_strike_string = f"{instrument}{lower_strike}{option_type}"
        else:
            print("Error: Instrument not recognized")
            return None
        return lower_strike_string
        
    def find_option_by_symbol(self, symbol):
        for option in self.option_chain:
            if symbol in option.get('symbol'):
                return option

if __name__ == "__main__":

    symbol = "NSE:BANKNIFTY-INDEX"
    options_chain = OptionsChain(symbol=symbol)

    option = options_chain.find_closest_option(target_ltp=90,option_type='PE')
    print(option['ltp'])
    print(option)