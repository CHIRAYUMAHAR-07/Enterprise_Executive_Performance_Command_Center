import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()
np.random.seed(42)

# Configuration
START_DATE = datetime(2022, 1, 1)
END_DATE = datetime(2025, 12, 31)
NUM_DAYS = (END_DATE - START_DATE).days

REGIONS = ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Middle East']
COUNTRIES = {
    'North America': ['USA', 'Canada', 'Mexico'],
    'Europe': ['UK', 'Germany', 'France', 'Spain', 'Italy'],
    'Asia Pacific': ['China', 'Japan', 'India', 'Australia', 'Singapore'],
    'Latin America': ['Brazil', 'Argentina', 'Chile', 'Colombia'],
    'Middle East': ['UAE', 'Saudi Arabia', 'Israel']
}

TEAMS = ['Sales', 'Marketing', 'Operations', 'Technology', 'Finance', 'HR']
PRODUCTS = ['Enterprise Suite', 'Cloud Platform', 'Analytics Pro', 'Security Plus', 'AI Services']
CUSTOMER_SEGMENTS = ['Enterprise', 'Mid-Market', 'SMB']

# 1. Generate Date Dimension
def generate_date_dimension():
    dates = pd.date_range(START_DATE, END_DATE, freq='D')
    
    date_dim = pd.DataFrame({
        'DateKey': dates.strftime('%Y%m%d').astype(int),
        'Date': dates,
        'Year': dates.year,
        'Quarter': dates.quarter,
        'Month': dates.month,
        'MonthName': dates.strftime('%B'),
        'Week': dates.isocalendar().week,
        'DayOfWeek': dates.dayofweek + 1,
        'DayName': dates.strftime('%A'),
        'IsWeekend': (dates.dayofweek >= 5).astype(int),
        'FiscalYear': (dates + pd.DateOffset(months=6)).year,  # Fiscal year starts July
        'FiscalQuarter': ((dates.month + 5) % 12 // 3) + 1
    })
    
    return date_dim

# 2. Generate Region Dimension
def generate_region_dimension():
    regions = []
    region_id = 1
    
    for region, countries in COUNTRIES.items():
        for country in countries:
            num_cities = random.randint(2, 4)
            for _ in range(num_cities):
                regions.append({
                    'RegionKey': region_id,
                    'Region': region,
                    'Country': country,
                    'City': fake.city(),
                    'RegionManager': fake.name()
                })
                region_id += 1
    
    return pd.DataFrame(regions)

# 3. Generate Team Dimension
def generate_team_dimension():
    teams = []
    team_id = 1
    
    for team in TEAMS:
        num_sub_teams = random.randint(3, 6)
        for i in range(num_sub_teams):
            teams.append({
                'TeamKey': team_id,
                'Department': team,
                'SubTeam': f'{team} - Team {i+1}',
                'TeamLead': fake.name(),
                'HeadCount': random.randint(10, 50)
            })
            team_id += 1
    
    return pd.DataFrame(teams)

# 4. Generate Product Dimension
def generate_product_dimension():
    products = []
    
    for idx, product in enumerate(PRODUCTS, 1):
        products.append({
            'ProductKey': idx,
            'ProductName': product,
            'Category': random.choice(['Software', 'Services', 'Platform']),
            'UnitPrice': random.randint(1000, 50000)
        })
    
    return pd.DataFrame(products)

# 5. Generate Revenue Fact Table
def generate_revenue_fact(date_dim, region_dim, team_dim, product_dim):
    revenue_records = []
    
    # Generate monthly aggregated data for performance
    for date in pd.date_range(START_DATE, END_DATE, freq='MS'):  # Month Start
        date_key = int(date.strftime('%Y%m%d'))
        
        # Generate 50-100 transactions per month
        num_transactions = random.randint(50, 100)
        
        for _ in range(num_transactions):
            region = region_dim.sample(1).iloc[0]
            team = team_dim.sample(1).iloc[0]
            product = product_dim.sample(1).iloc[0]
            
            # Add seasonality and growth trend
            base_revenue = product['UnitPrice'] * random.randint(1, 10)
            month_factor = 1 + 0.2 * np.sin(2 * np.pi * date.month / 12)  # Seasonality
            year_factor = 1 + 0.15 * (date.year - START_DATE.year)  # Growth
            noise = random.uniform(0.8, 1.2)
            
            revenue = base_revenue * month_factor * year_factor * noise
            
            revenue_records.append({
                'RevenueID': len(revenue_records) + 1,
                'DateKey': date_key,
                'RegionKey': region['RegionKey'],
                'TeamKey': team['TeamKey'],
                'ProductKey': product['ProductKey'],
                'Revenue': round(revenue, 2),
                'Units': random.randint(1, 20),
                'CustomerSegment': random.choice(CUSTOMER_SEGMENTS)
            })
    
    return pd.DataFrame(revenue_records)

# 6. Generate Cost Fact Table
def generate_cost_fact(date_dim, team_dim):
    cost_records = []
    
    for date in pd.date_range(START_DATE, END_DATE, freq='MS'):
        date_key = int(date.strftime('%Y%m%d'))
        
        for _, team in team_dim.iterrows():
            # Cost categories
            salary_cost = team['HeadCount'] * random.randint(5000, 12000)
            operational_cost = salary_cost * random.uniform(0.3, 0.6)
            
            # Add year-over-year cost increase
            year_factor = 1 + 0.05 * (date.year - START_DATE.year)
            
            cost_records.append({
                'CostID': len(cost_records) + 1,
                'DateKey': date_key,
                'TeamKey': team['TeamKey'],
                'SalaryCost': round(salary_cost * year_factor, 2),
                'OperationalCost': round(operational_cost * year_factor, 2),
                'TotalCost': round((salary_cost + operational_cost) * year_factor, 2)
            })
    
    return pd.DataFrame(cost_records)

# 7. Generate SLA Fact Table
def generate_sla_fact(date_dim, region_dim):
    sla_records = []
    
    for date in pd.date_range(START_DATE, END_DATE, freq='D'):
        date_key = int(date.strftime('%Y%m%d'))
        
        # Sample some regions for daily SLA metrics
        sampled_regions = region_dim.sample(n=min(10, len(region_dim)))
        
        for _, region in sampled_regions.iterrows():
            sla_records.append({
                'SLAID': len(sla_records) + 1,
                'DateKey': date_key,
                'RegionKey': region['RegionKey'],
                'ResponseTime': round(random.uniform(0.5, 5.0), 2),  # hours
                'ResolutionTime': round(random.uniform(2, 48), 2),  # hours
                'UpTime': round(random.uniform(95, 100), 2),  # percentage
                'TicketsResolved': random.randint(10, 100),
                'TicketsOpen': random.randint(5, 50),
                'SLATarget': 99.0,
                'SLAAchieved': round(random.uniform(96, 100), 2)
            })
    
    return pd.DataFrame(sla_records)

# 8. Generate Risk Fact Table
def generate_risk_fact(date_dim, region_dim, team_dim):
    risk_records = []
    risk_categories = ['Operational', 'Financial', 'Compliance', 'Strategic', 'Technology']
    
    for date in pd.date_range(START_DATE, END_DATE, freq='MS'):
        date_key = int(date.strftime('%Y%m%d'))
        
        # Generate 20-30 risk entries per month
        for _ in range(random.randint(20, 30)):
            region = region_dim.sample(1).iloc[0]
            team = team_dim.sample(1).iloc[0]
            
            risk_records.append({
                'RiskID': len(risk_records) + 1,
                'DateKey': date_key,
                'RegionKey': region['RegionKey'],
                'TeamKey': team['TeamKey'],
                'RiskCategory': random.choice(risk_categories),
                'RiskScore': random.randint(1, 10),  # 1-10 scale
                'Impact': random.choice(['Low', 'Medium', 'High', 'Critical']),
                'Probability': random.choice(['Low', 'Medium', 'High']),
                'MitigationStatus': random.choice(['Identified', 'In Progress', 'Mitigated', 'Accepted'])
            })
    
    return pd.DataFrame(risk_records)

# Main execution
if __name__ == '__main__':
    print("Generating Enterprise Executive Performance Data...")
    
    # Generate all dimensions
    print("1/8 Generating Date Dimension...")
    date_dim = generate_date_dimension()
    
    print("2/8 Generating Region Dimension...")
    region_dim = generate_region_dimension()
    
    print("3/8 Generating Team Dimension...")
    team_dim = generate_team_dimension()
    
    print("4/8 Generating Product Dimension...")
    product_dim = generate_product_dimension()
    
    # Generate all facts
    print("5/8 Generating Revenue Facts...")
    revenue_fact = generate_revenue_fact(date_dim, region_dim, team_dim, product_dim)
    
    print("6/8 Generating Cost Facts...")
    cost_fact = generate_cost_fact(date_dim, team_dim)
    
    print("7/8 Generating SLA Facts...")
    sla_fact = generate_sla_fact(date_dim, region_dim)
    
    print("8/8 Generating Risk Facts...")
    risk_fact = generate_risk_fact(date_dim, region_dim, team_dim)
    
    # Save to Excel with multiple sheets
    print("\nSaving data to Excel...")
    with pd.ExcelWriter('Enterprise_Performance_Data.xlsx', engine='openpyxl') as writer:
        date_dim.to_excel(writer, sheet_name='DimDate', index=False)
        region_dim.to_excel(writer, sheet_name='DimRegion', index=False)
        team_dim.to_excel(writer, sheet_name='DimTeam', index=False)
        product_dim.to_excel(writer, sheet_name='DimProduct', index=False)
        revenue_fact.to_excel(writer, sheet_name='FactRevenue', index=False)
        cost_fact.to_excel(writer, sheet_name='FactCost', index=False)
        sla_fact.to_excel(writer, sheet_name='FactSLA', index=False)
        risk_fact.to_excel(writer, sheet_name='FactRisk', index=False)
    
    # Print summary statistics
    print("\n" + "="*60)
    print("DATA GENERATION COMPLETE!")
    print("="*60)
    print(f"\nDate Range: {START_DATE.date()} to {END_DATE.date()}")
    print(f"Total Days: {NUM_DAYS}")
    print(f"\nDimensions Generated:")
    print(f"  - Date Records: {len(date_dim):,}")
    print(f"  - Regions: {len(region_dim):,}")
    print(f"  - Teams: {len(team_dim):,}")
    print(f"  - Products: {len(product_dim):,}")
    print(f"\nFacts Generated:")
    print(f"  - Revenue Transactions: {len(revenue_fact):,}")
    print(f"  - Cost Records: {len(cost_fact):,}")
    print(f"  - SLA Metrics: {len(sla_fact):,}")
    print(f"  - Risk Entries: {len(risk_fact):,}")
    print(f"\nTotal Records: {len(date_dim) + len(region_dim) + len(team_dim) + len(product_dim) + len(revenue_fact) + len(cost_fact) + len(sla_fact) + len(risk_fact):,}")
    print(f"\nFile saved: Enterprise_Performance_Data.xlsx")
    print("="*60)