import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def cleanup_database():
    # Load environment variables
    load_dotenv()
    
    # PostgreSQL connection details (matching docker-compose.yml)
    db_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'bitesoft_ai',
        'user': 'postgres',
        'password': 'postgres'
    }
    
    try:
        print(f"📂 Connecting to PostgreSQL at {db_config['host']}:{db_config['port']}...")
        conn = await asyncpg.connect(**db_config)
        
        # Check if tables exist
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
        """)
        table_names = [t['table_name'] for t in tables]
        print(f"📋 Found tables: {table_names}")
        
        # Delete from document_confirmations
        if 'document_confirmations' in table_names or 'documentconfirmation' in table_names:
            result = await conn.execute('DELETE FROM document_confirmations')
            print(f'🗑️  Cleared document_confirmations: {result}')
        else:
            print('⚠️  document_confirmations table not found')
        
        # Delete from audit_logs
        if 'audit_logs' in table_names or 'auditlog' in table_names:
            result = await conn.execute('DELETE FROM audit_logs')
            print(f'🗑️  Cleared audit_logs: {result}')
        else:
            print('⚠️  audit_logs table not found')
        
        # Run VACUUM to reclaim space
        await conn.execute('VACUUM ANALYZE')
        print('🧹 Ran VACUUM ANALYZE')
        
        await conn.close()
        print('✅ Database cleanup completed')
        
    except asyncpg.PostgresConnectionError as e:
        print(f'❌ Connection Error: {e}')
        print('💡 Make sure PostgreSQL is running: docker-compose up -d db')
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    asyncio.run(cleanup_database())