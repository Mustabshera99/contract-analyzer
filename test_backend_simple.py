#!/usr/bin/env python3
"""
Simple test script to debug backend issues
"""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_backend_imports():
    """Test if backend imports work without hanging."""
    print("🔧 Testing backend imports...")
    
    try:
        print("  - Importing config...")
        from backend.app.core.config import get_settings
        settings = get_settings()
        print(f"  ✅ Config loaded: {settings.database_url}")
        
        print("  - Importing database...")
        from backend.app.core.database import get_database_manager
        db_manager = await get_database_manager()
        print("  ✅ Database manager created")
        
        print("  - Importing document processor...")
        from backend.app.services.document_processor import DocumentProcessingService
        processor = DocumentProcessingService()
        print("  ✅ Document processor created")
        
        print("  - Testing simple document processing...")
        # Create a simple test file
        test_file = Path("test_simple.txt")
        test_file.write_text("This is a simple test contract.")
        
        try:
            result = processor.process_document(str(test_file), "test_simple.txt")
            print(f"  ✅ Document processed: {len(result.content)} characters")
        finally:
            test_file.unlink()  # Clean up
        
        print("  - Importing workflow service...")
        from backend.app.services.workflow_service import workflow_service
        print("  ✅ Workflow service imported")
        
        print("✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error during imports: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_simple_analysis():
    """Test a simple analysis workflow."""
    print("\n🔧 Testing simple analysis...")
    
    try:
        from backend.app.services.workflow_service import workflow_service
        
        # Start a simple analysis
        task_id = await workflow_service.start_analysis(
            contract_text="This is a test contract with some terms.",
            contract_filename="test.txt",
            timeout_seconds=10
        )
        print(f"  ✅ Analysis started: {task_id}")
        
        # Wait a bit and check status
        await asyncio.sleep(2)
        status = await workflow_service.get_task_status(task_id)
        print(f"  ✅ Status: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🚀 Starting backend diagnostic test...")
    print("=" * 50)
    
    # Test imports
    imports_ok = await test_backend_imports()
    if not imports_ok:
        print("\n❌ Import test failed. Backend has issues.")
        return False
    
    # Test analysis
    analysis_ok = await test_simple_analysis()
    if not analysis_ok:
        print("\n❌ Analysis test failed.")
        return False
    
    print("\n✅ All tests passed! Backend should work.")
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
