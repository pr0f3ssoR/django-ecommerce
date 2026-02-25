import stripe
import os
from dotenv import load_dotenv
from pprint import pprint


env = load_dotenv()

stripe.api_key = os.getenv('stripe_screte_key') if env else None

