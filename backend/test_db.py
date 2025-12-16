"""
Test script to verify database connection and table creation.
"""
import sys
import os
from sqlalchemy import text, inspect

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from database import engine, init_db
from config import settings
from models import Lead, LeadStatus, LeadSource

def test_connection():
    """Test database connection."""
    print("=" * 50)
    print("Testing Database Connection")
    print("=" * 50)
    print(f"Database URL: {settings.DATABASE_URL[:50]}...")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✓ Connection successful!")
            print(f"✓ PostgreSQL version: {version[:80]}...")
            return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

def test_tables():
    """Test table creation and listing."""
    print("\n" + "=" * 50)
    print("Testing Table Creation")
    print("=" * 50)
    
    try:
        # Initialize database (create tables)
        print("Creating tables...")
        init_db()
        print("✓ Tables created successfully!")
        
        # List all tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"\nTables in database:")
        for table in tables:
            print(f"  - {table}")
            # Show columns
            columns = inspector.get_columns(table)
            print(f"    Columns: {len(columns)}")
            for col in columns[:5]:  # Show first 5 columns
                print(f"      • {col['name']} ({col['type']})")
            if len(columns) > 5:
                print(f"      ... and {len(columns) - 5} more")
        
        return len(tables) > 0
    except Exception as e:
        print(f"✗ Table creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_write():
    """Test writing data to database."""
    print("\n" + "=" * 50)
    print("Testing Database Write")
    print("=" * 50)
    
    try:
        from database import SessionLocal
        
        # Create a test lead
        db = SessionLocal()
        test_lead = Lead(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            company_name="Test Company",
            source=LeadSource.API,
            status=LeadStatus.NEW
        )
        
        # Check if lead already exists
        existing = db.query(Lead).filter(Lead.email == "test@example.com").first()
        if existing:
            print("Test lead already exists, deleting...")
            db.delete(existing)
            db.commit()
        
        print("Adding test lead...")
        db.add(test_lead)
        db.commit()
        db.refresh(test_lead)
        
        print(f"✓ Test lead created with ID: {test_lead.id}")
        
        # Verify it was written
        verified = db.query(Lead).filter(Lead.id == test_lead.id).first()
        if verified:
            print(f"✓ Lead verified in database: {verified.email}")
            
            # Count all leads
            count = db.query(Lead).count()
            print(f"✓ Total leads in database: {count}")
            
            # Clean up
            db.delete(test_lead)
            db.commit()
            print("✓ Test lead cleaned up")
            
            db.close()
            return True
        else:
            print("✗ Could not verify lead in database")
            db.close()
            return False
            
    except Exception as e:
        print(f"✗ Write test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 50)
    print("DATABASE CONNECTIVITY TEST")
    print("=" * 50 + "\n")
    
    results = {}
    
    # Test 1: Connection
    results['connection'] = test_connection()
    
    # Test 2: Tables
    if results['connection']:
        results['tables'] = test_tables()
    else:
        results['tables'] = False
        print("\nSkipping table test due to connection failure")
    
    # Test 3: Write
    if results['connection'] and results['tables']:
        results['write'] = test_write()
    else:
        results['write'] = False
        print("\nSkipping write test due to previous failures")
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Connection Test: {'✓ PASS' if results['connection'] else '✗ FAIL'}")
    print(f"Table Test:      {'✓ PASS' if results['tables'] else '✗ FAIL'}")
    print(f"Write Test:      {'✓ PASS' if results['write'] else '✗ FAIL'}")
    
    if all(results.values()):
        print("\n✓ All tests passed! Database is working correctly.")
        return 0
    else:
        print("\n✗ Some tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
