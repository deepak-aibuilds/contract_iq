from app.llm import get_payment, get_termination, get_renewal

async def extract_payment(chunks):

    
    payment_chunk = next(
        (c for c in chunks if "PAYMENT" in c["section"].upper()),
        None
    )
    if not payment_chunk:
        return {
            "payment_terms": None,
            "raw_text": None,
            "note": None,
            "confidence": "low",
            "is_found": False
        }

    payment_chain = get_payment()
    payment_data = await payment_chain.ainvoke({
        'section_text': payment_chunk['content']
    })
    return payment_data


async def extract_termination(chunks):
    termination_chunk = next(
        (c for c in chunks if 'TERMINATION' in c['section'].upper()), None
    )
    if not termination_chunk:
        return{
            "notice_period": None,
            "termination_type": None,
            "conditions": None,
            "raw_text": None,
            "confidence": "low",
            "is_found": False
            }
    termination_chain = get_termination()
    termination_data = await termination_chain.ainvoke({
        'section_text': termination_chunk['content']

    })
    return termination_data



async def extract_renewal(chunks):
    for c in chunks:
        print(repr(c['section']))
  
    renewal_chunk = next(
    (c for c in chunks if any(
        keyword in c["section"].upper()
        for keyword in ["RENEWAL", "AUTO-RENEW"]
    )),
    None
        )
    print(renewal_chunk)
    if not renewal_chunk:
       return {
            "is_auto_renewal": False,
            "notice_required": None,
            "renewal_terms": None,
            "raw_text": None,
            "confidence": None,
            "is_found": False
            }
    renewal_chain = get_renewal()
    renewal_data = await renewal_chain.ainvoke({
        'section_text': renewal_chunk['content']
    })
    return renewal_data
    