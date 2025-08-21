"""
FSM states for partner registration in Karma System.
"""
from aiogram.fsm.state import State, StatesGroup

class PartnerRegistration(StatesGroup):
    """Partner registration FSM states."""
    company_data = State()      # Company name input
    description = State()       # Phone and business description
    offer_details = State()     # Category selection and offer details
    confirmation = State()      # Confirmation and offer details
    web_auth = State()         # Email and password for web panel
