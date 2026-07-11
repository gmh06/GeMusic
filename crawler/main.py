import os
import json
import asyncio
import argparse
from robot import login , robot

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--login", action="store_true", help="open the browser and save refreshed cookies to config.json")
    args = parser.parse_args()

    if args.login:
        asyncio.run(login())
        return
    
    print("Loading config.json...")
    
    if not os.path.exists("config.json"):
        raise FileNotFoundError("config.json not found. Please create config.json that contains headers information.")
    
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
        
    print("Finish loading config.json.")


    asyncio.run(robot(config))

if __name__ == "__main__":
    main()