def predict(case):
    # Heuristic-based simple rule set (simulate CE for demo)
    case_type, agreement, notice, consumer, matrimonial, value = case

    if case_type in ["Criminal", "Family", "Environmental", "PIL"]:
        return "Yes"
    if case_type == "Civil" and value == ">1L" and agreement == "Yes":
        return "Yes"
    if case_type == "Consumer" and consumer == "Yes" and value != "<10k":
        return "Yes"
    return "No"