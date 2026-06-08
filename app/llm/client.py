from langchain_mistralai import ChatMistralAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from pathlib import Path
from typing import Literal
from pydantic import BaseModel


load_dotenv()


class PaymentJson(BaseModel):
    payment_terms: str
    raw_text: str
    notes: str
    confidence : Literal['low','medium','high']
    is_found: bool

class TerminationJson(BaseModel):
    notice_period: str
    termination_type: Literal[
                                "for cause",
                                "for convenience",
                                "mutual",
                                "for cause and convenience",
                                'Unknown'
                                ]
    
    condition: str
    raw_text: str
    confidence : Literal['low','medium','high']
    is_found: bool

class RenewalJson(BaseModel):
    is_auto_renewal: bool | None = None
    notice_required: str | None = None
    renewal_terms: str | None = None
    raw_text: str | None = None
    confidence: str
    is_found: bool

def load_prompt(name: str) -> str:
    path = Path(__file__).parent /  f"{name}.txt"
    return path.read_text()


payment_extractor= load_prompt('prompts/payment_v1')
payment_prompt= ChatPromptTemplate.from_template(payment_extractor)

termination_extractor= load_prompt('prompts/termination_v1')
termination_prompt= ChatPromptTemplate.from_template(termination_extractor)



renewal_extractor= load_prompt('prompts/renewal_v1')
renewal_prompt= ChatPromptTemplate.from_template(renewal_extractor)


primary_llm  = ChatMistralAI(model="mistral-small-latest")
fallback_llm = ChatGroq(model="llama-3.3-70b-versatile")


llm = primary_llm.with_fallbacks([fallback_llm])


def get_payment():
    return payment_prompt | llm.with_structured_output(PaymentJson)

def get_termination():
    return termination_prompt | llm.with_structured_output(TerminationJson)

def get_renewal():
    return renewal_prompt | llm.with_structured_output(RenewalJson)