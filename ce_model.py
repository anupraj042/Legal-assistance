def predict(case):
    case_type, sub_type, agreement, notice, consumer, matrimonial, value = case
    if case_type in ["Criminal", "Family", "Environmental", "PIL"]:
        return "Yes", personalized_guidance(case_type)
    if case_type == "Civil" and value == ">1L" and agreement == "Yes":
        return "Yes", personalized_guidance(case_type)
    if case_type == "Consumer" and consumer == "Yes" and value != "<10k":
        return "Yes", personalized_guidance(case_type)
    return "No", "No legal action needed. Try mediation or informal resolution."

def personalized_guidance(case_type):
    suggestions = {
        "Civil": "You may consult a civil lawyer and file a suit in district court.",
        "Criminal": "Approach the nearest police station to file an FIR.",
        "Consumer": "Submit a complaint online via the National Consumer Helpline.",
        "Family": "Consult a family court advocate for divorce, custody, or maintenance matters.",
        "Environmental": "File a complaint with State Pollution Board or NGT.",
        "PIL": "Consult a legal NGO or advocate to draft a public interest litigation in High Court."
    }
    return suggestions.get(case_type, "Consult a legal advisor for next steps.")