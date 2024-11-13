from sqlalchemy import text
import streamlit as st
import numpy as np
from PIL import Image
import pickle
import io
import face_recognition
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from datetime import time
from datetime import datetime
import pytz
import re
import base64
from io import BytesIO
import pandas as pd
from fpdf import FPDF