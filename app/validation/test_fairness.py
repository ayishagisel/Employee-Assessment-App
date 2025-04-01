import unittest
from typing import List, Dict, Any
import random
from .fairness_validator import FairnessValidator, ValidationResult

class TestFairnessValidation(unittest.TestCase):
    def setUp(self):
        self.validator = FairnessValidator()
        self.mock_employee_data = self._generate_mock_employee_data()
        self.mock_results = self._generate_mock_results()

    def _generate_mock_employee_data(self) -> List[Dict[str, Any]]:
        """Generate mock employee data with diverse demographics."""
        departments = ["Engineering", "Sales", "Marketing", "HR", "Finance"]
        role_levels = ["Junior", "Mid", "Senior", "Lead", "Manager"]
        genders = ["Male", "Female", "Other"]
        
        employees = []
        for i in range(50):
            employee = {
                "id": f"emp_{i}",
                "name": f"Employee {i}",
                "gender": random.choice(genders),
                "department": random.choice(departments),
                "role_level": random.choice(role_levels),
                "performance_rating": random.uniform(1, 5)
            }
            employees.append(employee)
        
        return employees

    def _generate_mock_results(self) -> List[Dict[str, Any]]:
        """Generate mock assessment results with potential biases."""
        results = []
        
        for emp in self.mock_employee_data:
            # Introduce some bias in sentiment scores based on demographics
            base_sentiment = random.uniform(0.5, 0.9)
            
            # Add bias based on gender (example)
            if emp["gender"] == "Female":
                base_sentiment *= 0.9  # 10% lower for females
            
            # Add bias based on department (example)
            if emp["department"] == "Engineering":
                base_sentiment *= 1.1  # 10% higher for engineering
            
            result = {
                "employee_id": emp["id"],
                "sentiment_analysis": {
                    "sentiment_score": min(1.0, max(0.0, base_sentiment)),
                    "sentiment_label": "Positive" if base_sentiment > 0.6 else "Negative",
                    "confidence": random.uniform(0.7, 0.95),
                    "strengths": ["Communication", "Problem Solving", "Teamwork"]
                },
                "promotion_recommendation": {
                    "promotion_recommended": random.random() > 0.5,
                    "recommended_role": f"Senior {emp['department']}",
                    "confidence_score": random.uniform(0.7, 0.95),
                    "timeline": "6-12 months",
                    "rationale": "Strong performance and leadership potential",
                    "development_areas": ["Leadership", "Technical Skills"]
                }
            }
            results.append(result)
        
        return results

    def test_sentiment_bias_validation(self):
        """Test validation of sentiment analysis for biases."""
        results = self.validator.validate_sentiment_analysis(
            self.mock_results,
            self.mock_employee_data
        )
        
        self.assertIsInstance(results, list)
        self.assertTrue(all(isinstance(r, ValidationResult) for r in results))
        
        # Check if bias was detected in gender-based sentiment
        gender_bias = next(
            (r for r in results if r.metric_name == "sentiment_bias_gender"),
            None
        )
        self.assertIsNotNone(gender_bias)
        self.assertGreater(gender_bias.value, 0)

    def test_promotion_parity_validation(self):
        """Test validation of promotion recommendations for fairness."""
        results = self.validator.validate_promotion_recommendations(
            self.mock_results,
            self.mock_employee_data
        )
        
        self.assertIsInstance(results, list)
        self.assertTrue(all(isinstance(r, ValidationResult) for r in results))
        
        # Check if bias was detected in department-based promotions
        dept_bias = next(
            (r for r in results if r.metric_name == "promotion_parity_department"),
            None
        )
        self.assertIsNotNone(dept_bias)
        self.assertGreater(dept_bias.value, 0)

    def test_report_generation(self):
        """Test generation of validation report."""
        # Run all validations
        sentiment_results = self.validator.validate_sentiment_analysis(
            self.mock_results,
            self.mock_employee_data
        )
        promotion_results = self.validator.validate_promotion_recommendations(
            self.mock_results,
            self.mock_employee_data
        )
        
        self.validator.results = sentiment_results + promotion_results
        report = self.validator.generate_report()
        
        self.assertIn("timestamp", report)
        self.assertIn("total_validations", report)
        self.assertIn("passed_validations", report)
        self.assertIn("failed_validations", report)
        self.assertIn("metrics", report)
        
        # Check metrics structure
        self.assertIn("sentiment", report["metrics"])
        self.assertIn("promotion", report["metrics"])

    def test_edge_cases(self):
        """Test handling of edge cases."""
        # Test with empty results
        empty_results = self.validator.validate_sentiment_analysis([], [])
        self.assertEqual(len(empty_results), 0)
        
        # Test with single result
        single_result = [self.mock_results[0]]
        single_employee = [self.mock_employee_data[0]]
        single_results = self.validator.validate_sentiment_analysis(single_result, single_employee)
        self.assertGreater(len(single_results), 0)
        
        # Test with missing demographic data
        incomplete_data = self.mock_employee_data.copy()
        incomplete_data[0].pop("gender")
        incomplete_results = self.validator.validate_sentiment_analysis(
            self.mock_results,
            incomplete_data
        )
        self.assertGreater(len(incomplete_results), 0)

if __name__ == '__main__':
    unittest.main() 