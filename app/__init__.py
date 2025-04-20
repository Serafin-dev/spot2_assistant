# app/__init__.py
"""
Real Estate Chatbot Application

Este módulo proporciona una aplicación conversacional que utiliza LLMs para recopilar
información sobre requisitos inmobiliarios comerciales.
"""

from . import agents
from . import models
from . import utils
from .main import assistant

__version__ = "0.1.0"
