from utils import CmdParser, Scraper
import sys

def main():
    parser = CmdParser(sys.argv[1:])
    parsed_args = parser.parse()
    scraper = Scraper(
        urls=list(parsed_args.get('args', [])), 
        metadata=parsed_args.get('metadata', None),
        save_assets=parsed_args.get('with-assets', False)
    )
    scraper.run()

if __name__ == "__main__":
    main()
