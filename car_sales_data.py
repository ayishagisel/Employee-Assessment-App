import random
from faker import Faker
import csv
from vector_db import VectorDB

fake = Faker()

class Salesperson:
    def __init__(self, name, qualifications, sales_volume, total_revenue, customer_satisfaction, reviews):
        self.name = name
        self.qualifications = qualifications
        self.sales_volume = sales_volume
        self.total_revenue = total_revenue
        self.customer_satisfaction = customer_satisfaction
        self.reviews = reviews

def generate_qualification():
    # ... existing code ...
    return fake.sentence(nb_words=10)

def generate_sales_volume():
    # ... existing code ...
    return random.randint(5, 20)

def generate_total_revenue(sales_volume):
    # ... existing code ...
    return sales_volume * random.randint(20000, 50000)

def generate_customer_satisfaction():
    # ... existing code ...
    return round(random.uniform(3.5, 5.0), 1)

def generate_reviews(sales_volume):
    # ... existing code ...
    reviews = []
    for _ in range(sales_volume):
        reviews.append(fake.paragraph(nb_sentences=3))
    return reviews

def generate_salespeople():
    salespeople_names = ["Alice Smith", "Bob Johnson", "Charlie Lee", "Diana Patel", "Ethan Kim"]
    salespeople = []
    
    for name in salespeople_names:
        qualifications = generate_qualification()
        sales_volume = generate_sales_volume()
        total_revenue = generate_total_revenue(sales_volume)
        customer_satisfaction = generate_customer_satisfaction()
        reviews = generate_reviews(sales_volume)
        
        salesperson = Salesperson(name, qualifications, sales_volume, total_revenue, customer_satisfaction, reviews)
        salespeople.append(salesperson)

    return salespeople

def write_to_csv(salespeople, file_path):
    with open(file_path, mode='w', newline='') as csv_file:
        fieldnames = ['name', 'qualifications', 'sales_volume', 'total_revenue', 'customer_satisfaction', 'reviews']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        writer.writeheader()
        for salesperson in salespeople:
            writer.writerow({
                'name': salesperson.name,
                'qualifications': salesperson.qualifications,
                'sales_volume': salesperson.sales_volume,
                'total_revenue': salesperson.total_revenue,
                'customer_satisfaction': salesperson.customer_satisfaction,
                'reviews': '|'.join(salesperson.reviews)
            })

def generate_embeddings(salespeople):
    vector_db = VectorDB("salespeople", 384)
    
    for idx, salesperson in enumerate(salespeople):
        text = f"{salesperson.name} {salesperson.qualifications} {' '.join(salesperson.reviews)}"
        vector_db.add_vectors({
            "id": [str(idx)],
            "text": [text],
            "metadata": [{
                "name": salesperson.name,
                "qualifications": salesperson.qualifications,
                "sales_volume": salesperson.sales_volume,
                "total_revenue": salesperson.total_revenue,
                "customer_satisfaction": salesperson.customer_satisfaction,
                "reviews": salesperson.reviews
            }]
        })

def main():
    salespeople = generate_salespeople()
    write_to_csv(salespeople, 'car_sales_data.csv')
    generate_embeddings(salespeople)
    
    for salesperson in salespeople:
        print(f"Name: {salesperson.name}")
        print(f"Qualifications: {salesperson.qualifications}")
        print(f"Sales Volume: {salesperson.sales_volume}")  
        print(f"Total Revenue: ${salesperson.total_revenue:,}")
        print(f"Customer Satisfaction: {salesperson.customer_satisfaction}")
        print("Reviews:")
        for review in salesperson.reviews:
            print(f"- {review}")
        print()

if __name__ == "__main__":
    main() 