import logging
from typing import Dict, List, Any
import numpy as np
from dataclasses import dataclass
from datetime import datetime
from scipy import stats

@dataclass
class ValidationResult:
    metric_name: str
    value: float
    threshold: float
    passed: bool
    details: Dict[str, Any]

class FairnessValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.results = []
        
        # Define fairness thresholds
        self.thresholds = {
            "demographic_parity": 0.8,     # Minimum ratio between groups
            "equal_opportunity": 0.8,      # Equal promotion rates across groups
            "predictive_parity": 0.8,      # Equal positive predictive value
            "sentiment_bias": 0.2,         # Maximum difference in sentiment scores
            "performance_correlation": 0.3, # Maximum correlation between demographics and scores
            "intersectional_bias": 0.25,   # Maximum difference in intersectional analysis
            "confidence_disparity": 0.15   # Maximum disparity in confidence scores
        }

    def validate_sentiment_analysis(self, results: List[Dict[str, Any]], employee_data: List[Dict[str, Any]]) -> List[ValidationResult]:
        """Validate sentiment analysis for potential biases."""
        validation_results = []
        
        # Group results by demographic attributes
        groups = self._group_by_demographics(results, employee_data)
        
        # Calculate sentiment score differences between groups
        for attr, group_results in groups.items():
            sentiment_scores = {}
            confidence_scores = {}
            for group, group_data in group_results.items():
                scores = [r["sentiment_analysis"]["sentiment_score"] for r in group_data]
                conf_scores = [r["sentiment_analysis"]["confidence"] for r in group_data]
                sentiment_scores[group] = scores
                confidence_scores[group] = conf_scores
            
            # Calculate mean scores for each group
            mean_scores = {group: np.mean(scores) for group, scores in sentiment_scores.items()}
            mean_conf = {group: np.mean(scores) for group, scores in confidence_scores.items()}
            
            # Check for significant differences
            max_diff = max(mean_scores.values()) - min(mean_scores.values())
            conf_diff = max(mean_conf.values()) - min(mean_conf.values())
            
            # Basic demographic parity
            validation_results.append(ValidationResult(
                metric_name=f"sentiment_bias_{attr}",
                value=max_diff,
                threshold=self.thresholds["sentiment_bias"],
                passed=max_diff <= self.thresholds["sentiment_bias"],
                details={
                    "mean_scores": mean_scores,
                    "group_sizes": {group: len(scores) for group, scores in sentiment_scores.items()}
                }
            ))
            
            # Confidence score disparity
            validation_results.append(ValidationResult(
                metric_name=f"confidence_disparity_{attr}",
                value=conf_diff,
                threshold=self.thresholds["confidence_disparity"],
                passed=conf_diff <= self.thresholds["confidence_disparity"],
                details={
                    "mean_confidence": mean_conf,
                    "group_sizes": {group: len(scores) for group, scores in confidence_scores.items()}
                }
            ))
            
            # Performance correlation check
            if attr in ["department", "role_level"]:
                performance_correlation = self._check_performance_correlation(
                    sentiment_scores,
                    employee_data,
                    attr
                )
                validation_results.append(ValidationResult(
                    metric_name=f"performance_correlation_{attr}",
                    value=abs(performance_correlation),
                    threshold=self.thresholds["performance_correlation"],
                    passed=abs(performance_correlation) <= self.thresholds["performance_correlation"],
                    details={
                        "correlation": performance_correlation,
                        "interpretation": "Higher absolute values indicate stronger bias"
                    }
                ))
        
        # Add intersectional analysis
        intersectional_results = self._analyze_intersectional_bias(results, employee_data)
        validation_results.extend(intersectional_results)
        
        return validation_results

    def validate_promotion_recommendations(self, results: List[Dict[str, Any]], employee_data: List[Dict[str, Any]]) -> List[ValidationResult]:
        """Validate promotion recommendations for fairness."""
        validation_results = []
        
        # Group results by demographic attributes
        groups = self._group_by_demographics(results, employee_data)
        
        for attr, group_results in groups.items():
            # Calculate promotion rates and confidence scores
            promotion_rates = {}
            confidence_scores = {}
            performance_ratings = {}
            
            for group, group_data in group_results.items():
                promotions = sum(1 for r in group_data if r["promotion_recommendation"]["promotion_recommended"])
                rate = promotions / len(group_data) if group_data else 0
                promotion_rates[group] = rate
                
                conf_scores = [r["promotion_recommendation"]["confidence_score"] for r in group_data]
                confidence_scores[group] = np.mean(conf_scores) if conf_scores else 0
                
                # Get average performance ratings for each group
                emp_ids = [r["employee_id"] for r in group_data]
                ratings = [next((emp["performance_rating"] for emp in employee_data if emp["id"] == emp_id), None)
                          for emp_id in emp_ids]
                ratings = [r for r in ratings if r is not None]
                performance_ratings[group] = np.mean(ratings) if ratings else 0
            
            # Check demographic parity
            min_rate = min(promotion_rates.values())
            max_rate = max(promotion_rates.values())
            parity_ratio = min_rate / max_rate if max_rate > 0 else 0
            
            validation_results.append(ValidationResult(
                metric_name=f"promotion_parity_{attr}",
                value=parity_ratio,
                threshold=self.thresholds["demographic_parity"],
                passed=parity_ratio >= self.thresholds["demographic_parity"],
                details={
                    "promotion_rates": promotion_rates,
                    "group_sizes": {group: len(data) for group, data in group_results.items()}
                }
            ))
            
            # Check equal opportunity (promotion rate relative to performance)
            opportunity_scores = {}
            for group in promotion_rates:
                if performance_ratings[group] > 0:
                    opportunity_scores[group] = promotion_rates[group] / performance_ratings[group]
                else:
                    opportunity_scores[group] = 0
            
            min_opp = min(opportunity_scores.values())
            max_opp = max(opportunity_scores.values())
            opp_ratio = min_opp / max_opp if max_opp > 0 else 0
            
            validation_results.append(ValidationResult(
                metric_name=f"equal_opportunity_{attr}",
                value=opp_ratio,
                threshold=self.thresholds["equal_opportunity"],
                passed=opp_ratio >= self.thresholds["equal_opportunity"],
                details={
                    "opportunity_scores": opportunity_scores,
                    "performance_ratings": performance_ratings
                }
            ))
        
        return validation_results

    def _check_performance_correlation(self, sentiment_scores: Dict[str, List[float]], 
                                    employee_data: List[Dict[str, Any]], 
                                    attribute: str) -> float:
        """Check correlation between sentiment scores and performance metrics."""
        all_scores = []
        all_metrics = []
        
        for group, scores in sentiment_scores.items():
            for score in scores:
                all_scores.append(score)
                # Find corresponding employee performance
                metric = next((emp["performance_rating"] for emp in employee_data 
                             if emp[attribute] == group), None)
                if metric is not None:
                    all_metrics.append(metric)
        
        if len(all_scores) > 1 and len(all_metrics) > 1:
            correlation, _ = stats.pearsonr(all_scores, all_metrics)
            return correlation
        return 0.0

    def _analyze_intersectional_bias(self, results: List[Dict[str, Any]], 
                                   employee_data: List[Dict[str, Any]]) -> List[ValidationResult]:
        """Analyze intersectional bias across multiple demographic attributes."""
        validation_results = []
        
        # Create intersectional groups (e.g., gender + department)
        attributes = ["gender", "department", "role_level"]
        for i in range(len(attributes)):
            for j in range(i + 1, len(attributes)):
                attr1, attr2 = attributes[i], attributes[j]
                
                intersectional_scores = {}
                for result, emp in zip(results, employee_data):
                    group = f"{emp.get(attr1, 'unknown')}_{emp.get(attr2, 'unknown')}"
                    if group not in intersectional_scores:
                        intersectional_scores[group] = []
                    intersectional_scores[group].append(
                        result["sentiment_analysis"]["sentiment_score"]
                    )
                
                # Calculate mean scores for each intersectional group
                mean_scores = {
                    group: np.mean(scores) 
                    for group, scores in intersectional_scores.items() 
                    if len(scores) > 0
                }
                
                if mean_scores:
                    max_diff = max(mean_scores.values()) - min(mean_scores.values())
                    
                    validation_results.append(ValidationResult(
                        metric_name=f"intersectional_bias_{attr1}_{attr2}",
                        value=max_diff,
                        threshold=self.thresholds["intersectional_bias"],
                        passed=max_diff <= self.thresholds["intersectional_bias"],
                        details={
                            "mean_scores": mean_scores,
                            "group_sizes": {
                                group: len(scores) 
                                for group, scores in intersectional_scores.items()
                            }
                        }
                    ))
        
        return validation_results

    def _group_by_demographics(self, results: List[Dict[str, Any]], 
                             employee_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """Group results by demographic attributes."""
        groups = {}
        
        # Create mapping of employee IDs to their data
        employee_map = {emp["id"]: emp for emp in employee_data}
        
        # Group results by each demographic attribute
        for attr in ["gender", "department", "role_level"]:
            groups[attr] = {}
            for result in results:
                emp_id = result["employee_id"]
                if emp_id in employee_map:
                    group = employee_map[emp_id].get(attr, "unknown")
                    if group not in groups[attr]:
                        groups[attr][group] = []
                    groups[attr][group].append(result)
        
        return groups

    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive validation report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_validations": len(self.results),
            "passed_validations": sum(1 for r in self.results if r.passed),
            "failed_validations": sum(1 for r in self.results if not r.passed),
            "metrics": {}
        }
        
        # Group results by metric type
        for result in self.results:
            metric_type = result.metric_name.split("_")[0]
            if metric_type not in report["metrics"]:
                report["metrics"][metric_type] = []
            
            # Convert numpy types to Python native types
            details = {}
            for key, value in result.details.items():
                if isinstance(value, dict):
                    details[key] = {k: float(v) if hasattr(v, 'dtype') else v 
                                  for k, v in value.items()}
                else:
                    details[key] = float(value) if hasattr(value, 'dtype') else value
            
            report["metrics"][metric_type].append({
                "name": result.metric_name,
                "value": float(result.value),
                "threshold": float(result.threshold),
                "passed": bool(result.passed),
                "details": details
            })
        
        return report

    def log_results(self):
        """Log validation results."""
        report = self.generate_report()
        
        self.logger.info("=== Validation Report ===")
        self.logger.info(f"Total Validations: {report['total_validations']}")
        self.logger.info(f"Passed: {report['passed_validations']}")
        self.logger.info(f"Failed: {report['failed_validations']}")
        
        for metric_type, results in report["metrics"].items():
            self.logger.info(f"\n{metric_type.upper()} Metrics:")
            for result in results:
                status = "PASSED" if result["passed"] else "FAILED"
                self.logger.info(f"- {result['name']}: {status}")
                self.logger.info(f"  Value: {result['value']:.3f} (Threshold: {result['threshold']})")
                self.logger.info(f"  Details: {result['details']}") 