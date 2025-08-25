import os
import types

from dotenv import load_dotenv

load_dotenv()

def env_str(name: str, default: str) -> str:
    return os.environ.get(name, default)


def env_bool(name: str, default: str) -> bool:
    return os.environ.get(name, default).lower() in ("1", "true", "yes")


timestamp_format = '%Y%m%dT%H%M%S'

output_root = env_str("CONFIG_OUTPUT_ROOT", "output")

# overridable per pipeline
use_proxies = env_bool("CONFIG_USE_PROXIES", "false")
use_proxies_for_pipeline = {
    "statusinvest": True,
    "simplywall": True,
}

# if True, global pipelines will throw away non-requested tickers
only_requested_tickers = env_bool("CONFIG_ONLY_REQUESTED_TICKERS", "false")

# if True, screenshots are kept under debug/processed (takes disk space quickly)
keep_debug_images = env_bool("CONFIG_KEEP_DEBUG_IMAGES", "false")

# data older than this is considered stale and should be scraped again
refresh_days = 30

# maximum number of error logs or files in debug/failed before giving up on a pipeline for particular ticker
# after refresh_days, error logs and files are ignored
error_limit = 8

# external dependencies

proxy_urls = [
    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks4/data.txt",
    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks5/data.txt",
    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/countries/US/data.txt",
    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/http/data.txt",
    "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/all/data.txt",
]

# visual_llm_model = "gemini-1.5-flash"
# visual_llm_model = "gemini-2.0-flash-lite" # tradingview and tipranks work
# visual_llm_model = "gemini-2.0-flash"
visual_llm_model = "gemini-2.5-flash-preview-05-20"  # investidor10 works
# visual_llm_model = "gemini-2.5-pro-preview-05-06"


def print_me():
    print("# config")
    for k, v in globals().items():
        if not k.startswith("__") and not callable(v) and not isinstance(v, types.ModuleType):
            print(f"{k}: {v}")
    print()
