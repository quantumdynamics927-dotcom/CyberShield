import argparse
from agents.metatron import run_agent

def main():
    p = argparse.ArgumentParser(prog="cyberlab-assistant")
    p.add_argument("-t", "--target", required=True, help="IP or hostname to scan")
    args = p.parse_args()
    print(run_agent(args.target))

if __name__ == "__main__":
    main()
