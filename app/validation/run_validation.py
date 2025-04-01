import logging
import json
from datetime import datetime
from pathlib import Path
from .fairness_validator import FairnessValidator
from .test_fairness import TestFairnessValidation

def setup_logging():
    """Configure logging for validation results."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"validation_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def run_validation():
    """Run validation tests and generate reports."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Run unit tests
    logger.info("Running fairness validation tests...")
    test_suite = TestFairnessValidation()
    test_suite.setUp()
    
    # Run sentiment analysis validation
    sentiment_results = test_suite.validator.validate_sentiment_analysis(
        test_suite.mock_results,
        test_suite.mock_employee_data
    )
    
    # Run promotion recommendations validation
    promotion_results = test_suite.validator.validate_promotion_recommendations(
        test_suite.mock_results,
        test_suite.mock_employee_data
    )
    
    # Combine results
    test_suite.validator.results = sentiment_results + promotion_results
    
    # Generate and save report
    report = test_suite.validator.generate_report()
    
    # Save report to JSON file
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = reports_dir / f"validation_report_{timestamp}.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Log results
    test_suite.validator.log_results()
    
    logger.info(f"Validation report saved to: {report_file}")
    
    # Print summary
    print("\nValidation Summary:")
    print(f"Total Validations: {report['total_validations']}")
    print(f"Passed: {report['passed_validations']}")
    print(f"Failed: {report['failed_validations']}")
    
    if report['failed_validations'] > 0:
        print("\nFailed Validations:")
        for metric_type, results in report['metrics'].items():
            for result in results:
                if not result['passed']:
                    print(f"- {result['name']}: {result['value']:.3f} (Threshold: {result['threshold']})")

if __name__ == '__main__':
    run_validation() 