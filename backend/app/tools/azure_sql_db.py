import pyodbc


AZURE_SQL_SERVER_NAME="mysqlserver0412.database.windows.net"
AZURE_SQL_DATABASE_NAME="user_db"
AZURE_SQL_USER_NAME="simclass_admin"
AZURE_SQL_PASSWORD="Hackathon123"
DRIVER="{ODBC Driver 18 for SQL Server}"

connection_string = f"DRIVER={DRIVER}; \
    SERVER={AZURE_SQL_SERVER_NAME}; \
    DATABASE={AZURE_SQL_DATABASE_NAME}; \
    UID={AZURE_SQL_USER_NAME}; \
    PWD={AZURE_SQL_PASSWORD};"


conn = pyodbc.connect(connection_string)

cursor = conn.cursor()

# cursor.execute('''
#     CREATE TABLE users (
#     id INT PRIMARY KEY IDENTITY(1,1),
#     nickname NVARCHAR(50) NOT NULL,         
#     avatar_url NVARCHAR(512),          
#     created_at DATETIME DEFAULT GETDATE(),
#     updated_at DATETIME DEFAULT GETDATE()
#     );
               
#     CREATE TABLE auth (
#     id INT PRIMARY KEY IDENTITY(1,1),
#     user_id INT NOT NULL FOREIGN KEY REFERENCES users(id) ON DELETE CASCADE,
#     identity_type VARCHAR(20) NOT NULL,  -- 登录类型
#     identifier NVARCHAR(255) NOT NULL,   -- 唯一标识
#     credential NVARCHAR(512),            -- 密码/Token
#     verified BIT DEFAULT 0,              -- 是否已验证
    
#     -- 组合唯一约束
#     UNIQUE (identity_type, identifier),
    
#     -- 索引优化
#     INDEX idx_identity (identity_type, identifier)
#     );
# ''')
# conn.commit()

