import chromadb
from chromadb.config import Settings
from app.models.assessment import Assessment
from app import db

class ChromaDBService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=".chroma_db")
        self.collection = self.client.get_or_create_collection(name="employee_assessments")

    def sync_assessments(self):
        assessments = Assessment.query.all()
        documents = []
        metadatas = []
        ids = []
        
        for assessment in assessments:
            text_content = f"""
            Employee: {assessment.employee_name}
            Position: {assessment.position}
            Strengths: {assessment.strengths}
            Areas for Improvement: {assessment.areas_for_improvement}
            Goals: {assessment.goals}
            Comments: {assessment.comments}
            """
            
            documents.append(text_content)
            metadatas.append({
                "assessment_id": str(assessment.id),
                "employee_name": assessment.employee_name,
                "position": assessment.position,
                "department": assessment.department,
                "review_period": assessment.review_period,
                "performance_rating": assessment.performance_rating
            })
            ids.append(str(assessment.id))
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def search_assessments(self, query, limit=5):
        results = self.collection.query(
            query_texts=[query],
            n_results=limit
        )
        return results

    def get_assessment_by_id(self, assessment_id):
        return Assessment.query.get(int(assessment_id))

    def sync_new_assessment(self, assessment):
        text_content = f"""
        Employee: {assessment.employee_name}
        Position: {assessment.position}
        Strengths: {assessment.strengths}
        Areas for Improvement: {assessment.areas_for_improvement}
        Goals: {assessment.goals}
        Comments: {assessment.comments}
        """
        
        self.collection.add(
            documents=[text_content],
            metadatas=[{
                "assessment_id": str(assessment.id),
                "employee_name": assessment.employee_name,
                "position": assessment.position,
                "department": assessment.department,
                "review_period": assessment.review_period,
                "performance_rating": assessment.performance_rating
            }],
            ids=[str(assessment.id)]
        )