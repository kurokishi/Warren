import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import pandas as pd
from typing import List, Dict
import time

class NewsSentimentAnalyzer:
    """
    News sentiment analysis
