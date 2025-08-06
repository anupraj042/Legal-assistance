"""
Candidate Elimination Algorithm for Legal Case Classification
This module implements the Candidate Elimination algorithm to learn legal case patterns
from training data and make predictions about whether legal action is needed.
"""

import pandas as pd
import copy

def load_cases(path):
    return pd.read_csv(path)

def predict_legal_issue(case_dict, dataset):
    # Match closest row from dataset (simulate CE for now)
    for _, row in dataset.iterrows():
        if all(str(row.get(k, "")).lower() == v.lower() for k, v in case_dict.items() if k in row):
            return row["Legal Issue"], get_guidance(row["Case Type"])
    return "No", "Try mediation or informal resolution."

def get_guidance(case_type):
    guidance_map = {
        "Civil": "Consult a civil lawyer or file a civil suit.",
        "Criminal": "Approach the police or file an FIR.",
        "Consumer": "File a case at your local Consumer Court.",
        "Family": "Consult a family court advocate.",
        "Environmental": "File a complaint with NGT.",
        "PIL": "File a PIL in High Court or Supreme Court."
    }
    return guidance_map.get(case_type, "Consult a legal expert.")

class CandidateElimination:
    def __init__(self):
        self.attributes = [
            'Case Type', 'Sub-Type', 'Value Involved', 
            'Agreement Signed', 'Notice Given', 
            'Consumer Complaint', 'Matrimonial Issue'
        ]
        self.specific_hypothesis = None
        self.general_hypotheses = None
        self.trained = False
        
    def initialize_hypotheses(self, num_attributes):
        """Initialize specific and general hypotheses"""
        # Specific hypothesis starts with most specific (all nulls)
        self.specific_hypothesis = ['∅'] * num_attributes
        
        # General hypotheses start with most general (all '?')
        self.general_hypotheses = [['?'] * num_attributes]
        
    def is_consistent(self, hypothesis, example, target):
        """Check if hypothesis is consistent with example"""
        for i, (h_val, e_val) in enumerate(zip(hypothesis, example)):
            if h_val != '?' and h_val != '∅' and h_val != e_val:
                return False
        return True
    
    def is_more_general(self, h1, h2):
        """Check if h1 is more general than h2"""
        for i, (v1, v2) in enumerate(zip(h1, h2)):
            if v2 != '∅' and v1 != '?' and v1 != v2:
                return False
        return True
    
    def is_more_specific(self, h1, h2):
        """Check if h1 is more specific than h2"""
        return self.is_more_general(h2, h1)
    
    def generalize_specific(self, specific, example):
        """Generalize specific hypothesis to cover positive example"""
        new_specific = copy.deepcopy(specific)
        for i, (s_val, e_val) in enumerate(zip(specific, example)):
            if s_val == '∅':
                new_specific[i] = e_val
            elif s_val != e_val:
                new_specific[i] = '?'
        return new_specific
    
    def specialize_general(self, general, example):
        """Specialize general hypothesis to exclude negative example"""
        specialized = []
        for hypothesis in general:
            for i, (h_val, e_val) in enumerate(zip(hypothesis, example)):
                if h_val == '?' and e_val is not None:
                    # Create specialized versions
                    # Get all possible values for this attribute from training data
                    possible_values = self.get_possible_values(i, e_val)
                    for val in possible_values:
                        new_h = copy.deepcopy(hypothesis)
                        new_h[i] = val
                        specialized.append(new_h)
                elif h_val == e_val:
                    # This hypothesis covers the negative example, remove it
                    break
            else:
                # If we didn't break, keep the original hypothesis
                specialized.append(hypothesis)
        return specialized
    
    def get_possible_values(self, attribute_index, exclude_value):
        """Get possible values for an attribute excluding the given value"""
        if not hasattr(self, 'training_data'):
            return []
        
        attribute_name = self.attributes[attribute_index]
        unique_values = self.training_data[attribute_name].unique()
        return [val for val in unique_values if val != exclude_value and pd.notna(val)]
    
    def remove_inconsistent_hypotheses(self, hypotheses, example, target):
        """Remove hypotheses that are inconsistent with the example"""
        return [h for h in hypotheses if self.is_consistent(h, example, target)]
    
    def remove_redundant_hypotheses(self, hypotheses):
        """Remove hypotheses that are more general than others"""
        filtered = []
        for i, h1 in enumerate(hypotheses):
            is_redundant = False
            for j, h2 in enumerate(hypotheses):
                if i != j and self.is_more_general(h1, h2):
                    is_redundant = True
                    break
            if not is_redundant:
                filtered.append(h1)
        return filtered
    
    def train(self, csv_file_path):
        """Train the Candidate Elimination algorithm on legal case data"""
        try:
            # Load training data
            self.training_data = pd.read_csv(csv_file_path)
            
            # Initialize hypotheses
            num_attributes = len(self.attributes)
            self.initialize_hypotheses(num_attributes)
            
            print("🎯 Training Candidate Elimination Algorithm...")
            print(f"📊 Training on {len(self.training_data)} legal cases")
            print("-" * 60)
            
            # Separate positive and negative examples for better processing
            positive_examples = []
            negative_examples = []
            
            for index, row in self.training_data.iterrows():
                example = [
                    row['Case Type'], row['Sub-Type'], row['Value Involved'],
                    row['Agreement Signed'], row['Notice Given'],
                    row['Consumer Complaint'], row['Matrimonial Issue']
                ]
                
                # Convert NaN to None for easier handling
                example = [None if pd.isna(val) else str(val) for val in example]
                target = str(row['Legal Issue']) if pd.notna(row['Legal Issue']) else 'No'
                
                if target == 'Yes':
                    positive_examples.append((example, index + 1))
                else:
                    negative_examples.append((example, index + 1))
            
            print(f"📊 Found {len(positive_examples)} positive and {len(negative_examples)} negative examples")
            print("-" * 60)
            
            # Process positive examples first
            print("🟢 Processing positive examples...")
            for example, case_num in positive_examples:
                print(f"Processing case {case_num}: {example} -> Yes")
                
                # Generalize specific hypothesis
                self.specific_hypothesis = self.generalize_specific(self.specific_hypothesis, example)
                
                # Remove inconsistent general hypotheses
                self.general_hypotheses = self.remove_inconsistent_hypotheses(
                    self.general_hypotheses, example, 'Yes'
                )
                
                print(f"   Specific: {self.specific_hypothesis}")
                print(f"   General:  {len(self.general_hypotheses)} hypotheses")
                print()
            
            # Process negative examples
            print("🔴 Processing negative examples...")
            for example, case_num in negative_examples:
                print(f"Processing case {case_num}: {example} -> No")
                
                # Check if specific hypothesis is consistent
                if not self.is_consistent(self.specific_hypothesis, example, 'No'):
                    print(f"   ✅ Specific hypothesis correctly excludes this negative example")
                else:
                    print(f"   ⚠️  Specific hypothesis incorrectly covers this negative example")
                
                # Specialize general hypotheses
                old_count = len(self.general_hypotheses)
                self.general_hypotheses = self.specialize_general(self.general_hypotheses, example)
                self.general_hypotheses = self.remove_redundant_hypotheses(self.general_hypotheses)
                
                print(f"   General hypotheses: {old_count} -> {len(self.general_hypotheses)}")
                print()
            
            # If we have no general hypotheses, create some basic ones based on the specific hypothesis
            if len(self.general_hypotheses) == 0:
                print("🔧 No general hypotheses remain. Creating fallback patterns...")
                self.create_fallback_hypotheses()
            
            self.trained = True
            print("✅ Training completed!")
            print(f"📋 Final Specific Hypothesis: {self.specific_hypothesis}")
            print(f"📋 Final General Hypotheses: {len(self.general_hypotheses)} patterns")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during training: {str(e)}")
            return False
    
    def create_fallback_hypotheses(self):
        """Create fallback hypotheses when no general hypotheses remain"""
        # Create hypotheses based on common legal patterns observed in the data
        fallback_patterns = [
            # Criminal cases are usually legal issues
            ['Criminal', '?', '?', '?', '?', '?', '?'],
            # Family cases with matrimonial issues
            ['Family', '?', '?', '?', '?', '?', 'Yes'],
            # Environmental cases are usually legal issues
            ['Environmental', '?', '?', '?', '?', '?', '?'],
            # PIL cases are usually legal issues
            ['PIL', '?', '?', '?', '?', '?', '?'],
            # High-value civil cases with agreements
            ['Civil', '?', '>50k', 'Yes', '?', '?', '?'],
            # Consumer cases with complaints
            ['Consumer', '?', '?', '?', '?', 'Yes', '?']
        ]
        
        self.general_hypotheses = fallback_patterns
        print(f"   Created {len(fallback_patterns)} fallback hypotheses based on legal patterns")
    
    def predict(self, case_data):
        """Predict whether legal action is needed for a given case"""
        if not self.trained:
            return "Error: Model not trained", "Please train the model first."
        
        try:
            # Convert case data to the same format as training data
            example = [str(val) if val is not None else None for val in case_data]
            
            # Check if specific hypothesis covers the example
            specific_covers = self.is_consistent(self.specific_hypothesis, example, 'Yes')
            
            # Check how many general hypotheses cover the example
            matching_general = [
                h for h in self.general_hypotheses 
                if self.is_consistent(h, example, 'Yes')
            ]
            
            general_coverage = len(matching_general) / len(self.general_hypotheses) if self.general_hypotheses else 0
            
            # Enhanced decision logic with pattern-based scoring
            pattern_score = self.calculate_pattern_score(example)
            
            # Combine different scoring methods
            if specific_covers and general_coverage > 0.5 and pattern_score > 0.7:
                prediction = "Yes"
                confidence = "High"
            elif (specific_covers and general_coverage > 0.3) or pattern_score > 0.6:
                prediction = "Yes"
                confidence = "Medium"
            elif general_coverage > 0.2 or pattern_score > 0.4:
                prediction = "Yes"
                confidence = "Low"
            elif general_coverage > 0.1 or pattern_score > 0.2:
                prediction = "Maybe"
                confidence = "Medium"
            else:
                prediction = "No"
                confidence = "High"
            
            # Generate guidance based on case type and matching patterns
            guidance = self.generate_guidance(case_data, prediction, confidence, matching_general)
            
            return prediction, guidance
            
        except Exception as e:
            return "Error", f"Prediction failed: {str(e)}"
    
    def calculate_pattern_score(self, example):
        """Calculate a pattern-based score for legal action likelihood"""
        score = 0.0
        case_type = example[0] if example else None
        sub_type = example[1] if len(example) > 1 else None
        value = example[2] if len(example) > 2 else None
        agreement = example[3] if len(example) > 3 else None
        notice = example[4] if len(example) > 4 else None
        consumer = example[5] if len(example) > 5 else None
        matrimonial = example[6] if len(example) > 6 else None
        
        # Case type scoring (based on training data patterns)
        case_type_scores = {
            'Criminal': 0.9,  # Almost always legal action needed
            'Environmental': 0.8,  # Usually legal action needed
            'PIL': 0.8,  # Usually legal action needed
            'Family': 0.7,  # Often legal action needed
            'Civil': 0.4,  # Mixed results
            'Consumer': 0.3  # Often resolved without legal action
        }
        
        if case_type in case_type_scores:
            score += case_type_scores[case_type] * 0.4
        
        # Sub-type specific patterns
        high_action_subtypes = ['Domestic Violence', 'Dowry Harassment', 'Theft', 'Pollution', 'Illegal Mining']
        if sub_type in high_action_subtypes:
            score += 0.2
        
        # Value-based scoring
        if value == '>50k' or value == '>1L':
            score += 0.15
        elif value == '10k-50k' or value == '10k–1L':
            score += 0.1
        elif value == '<10k':
            score += 0.05
        
        # Agreement and notice patterns
        if agreement == 'Yes':
            score += 0.1
        if notice == 'Yes':
            score += 0.1
        
        # Consumer complaint factor
        if consumer == 'Yes':
            score += 0.05
        
        # Matrimonial issue factor
        if matrimonial == 'Yes':
            score += 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def generate_guidance(self, case_data, prediction, confidence, matching_patterns=None):
        """Generate personalized legal guidance"""
        case_type = case_data[0] if case_data else "Unknown"
        sub_type = case_data[1] if len(case_data) > 1 else "Unknown"
        value = case_data[2] if len(case_data) > 2 else None
        
        guidance_map = {
            "Civil": "Consider consulting a civil lawyer and filing a suit in district court.",
            "Criminal": "Approach the nearest police station to file an FIR immediately.",
            "Consumer": "Submit a complaint online via the National Consumer Helpline.",
            "Family": "Consult a family court advocate for divorce, custody, or maintenance matters.",
            "Environmental": "File a complaint with State Pollution Board or National Green Tribunal.",
            "PIL": "Consult a legal NGO or advocate to draft a public interest litigation."
        }
        
        base_guidance = guidance_map.get(case_type, "Consult a legal advisor for next steps.")
        
        # Add specific sub-type guidance
        specific_guidance = ""
        if case_type == "Criminal":
            if sub_type in ["Domestic Violence", "Dowry Harassment"]:
                specific_guidance = " Consider contacting women's helpline (1091) for immediate support."
            elif sub_type == "Theft":
                specific_guidance = " Gather evidence and witness statements before filing FIR."
        elif case_type == "Consumer":
            specific_guidance = " Keep all receipts and communication records as evidence."
        elif case_type == "Environmental":
            specific_guidance = " Document environmental damage with photos and videos."
        
        # Add value-based insights
        value_insight = ""
        if value == '>50k' or value == '>1L':
            value_insight = " High-value case - consider hiring experienced counsel."
        elif value == '10k-50k' or value == '10k–1L':
            value_insight = " Medium-value case - cost-benefit analysis recommended."
        
        # Add pattern-based insights
        pattern_insight = ""
        if matching_patterns:
            pattern_count = len(matching_patterns)
            if pattern_count > 0:
                pattern_insight = f" (Matches {pattern_count} legal patterns)"
        
        # Calculate pattern score for additional context
        pattern_score = self.calculate_pattern_score(case_data)
        score_context = f" [Pattern Score: {pattern_score:.2f}]"
        
        if prediction == "Yes":
            return f"Legal action recommended ({confidence} confidence){pattern_insight}{score_context}. {base_guidance}{specific_guidance}{value_insight}"
        elif prediction == "Maybe":
            return f"Legal action may be needed ({confidence} confidence){pattern_insight}{score_context}. {base_guidance} Consider getting a second opinion.{specific_guidance}{value_insight}"
        else:
            return f"Legal action may not be necessary ({confidence} confidence){score_context}. Try mediation or informal resolution first. If issues persist, {base_guidance.lower()}{specific_guidance}"
    
    def get_model_summary(self):
        """Get a summary of the trained model"""
        if not self.trained:
            return "Model not trained yet."
        
        summary = f"""
🎯 Candidate Elimination Model Summary
=====================================
📊 Attributes: {len(self.attributes)}
📋 Specific Hypothesis: {self.specific_hypothesis}
📋 General Hypotheses: {len(self.general_hypotheses)} patterns learned

🔍 Attribute Mapping:
"""
        for i, attr in enumerate(self.attributes):
            summary += f"   {i}: {attr}\n"
        
        return summary

# Global instance for the Flask app
ce_model = CandidateElimination()

def train_model():
    """Train the candidate elimination model"""
    return ce_model.train('d:/Legal-assistance/minimal_legal_cases.csv')

def predict(case_data):
    """Make prediction using the trained model"""
    return ce_model.predict(case_data)

def get_model_info():
    """Get information about the trained model"""
    return ce_model.get_model_summary()

if __name__ == "__main__":
    # Train and test the model
    print("🚀 Starting Candidate Elimination Training...")
    
    if train_model():
        print("\n" + get_model_info())
        
        # Test with a sample case
        test_case = ["Civil", "Property Dispute", ">1L", "Yes", "Yes", "No", "No"]
        result, guidance = predict(test_case)
        print(f"\n🧪 Test Case: {test_case}")
        print(f"📊 Prediction: {result}")
        print(f"💡 Guidance: {guidance}")
    else:
        print("❌ Training failed!")