__all__ = ['CmdParser']
import argparse
import sys
from typing import List, Dict, Any

class CustomArgParser(argparse.ArgumentParser):
    def error(self, message: str):
        self.print_help(sys.stderr)
        sys.stderr.write('\nError: %s\n' % message)
        sys.exit(2)

class CmdParser:
    def __init__(self, args):
        self.parser = CustomArgParser()
        self.parser.add_argument('args', nargs='*', default=[])
        self.parser.add_argument('--metadata', type=str)
        self.parser.add_argument('--with-assets', action='store_true')
        self.args = self.parser.parse_args(args)
    #end def

    def parse(self) -> Dict[str, Any]:
        urls = self.sanitize_urls(self.args.args)
        return {
            'args': urls,
            'metadata': self.sanitize_url(self.args.metadata) if self.args.metadata else None,
            'with-assets': self.args.with_assets
        }
    #end def
    
    def sanitize_urls(self, urls: List[str]) -> List[str]:
        sanitized_urls = []
        for url in urls:
            sanitized_urls.append(self.sanitize_url(url))
        #end for
        return sanitized_urls
    #end def

    def sanitize_url(self, url: str) -> str:
        VALID_URL_PREFIXES = ['http', 'https', 'www']
        if any(url.startswith(prefix) for prefix in VALID_URL_PREFIXES):
            return url
        else:
            return f'www.{url}'
        #end if
    #end def

