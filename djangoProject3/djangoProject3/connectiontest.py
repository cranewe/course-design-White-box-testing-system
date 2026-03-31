import pyodbc
import sys

def test_sqlserver_connection():
    """测试SQL Server数据库连接"""
    
    # 数据库连接参数
    server = 'localhost'  # 或者您的SQL Server服务器地址
    database = 'ruanjian'
    username = 'root'
    password = '123'
    
    # 构建连接字符串
    # 使用SQL Server身份验证
    connection_string = f'''
    DRIVER={{ODBC Driver 17 for SQL Server}};
    SERVER={server};
    DATABASE={database};
    UID={username};
    PWD={password};
    '''
    
    try:
        print("正在尝试连接SQL Server数据库...")
        print(f"服务器: {server}")
        print(f"数据库: {database}")
        print(f"用户名: {username}")
        print("-" * 40)
        
        # 建立连接
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # 测试查询
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        
        print("✅ 数据库连接成功!")
        print(f"SQL Server版本: {version}")
        
        # 获取数据库信息
        cursor.execute("SELECT DB_NAME()")
        current_db = cursor.fetchone()[0]
        print(f"当前数据库: {current_db}")
        
        # 关闭连接
        cursor.close()
        conn.close()
        print("✅ 连接已正常关闭")
        
        return True
        
    except pyodbc.Error as e:
        print("❌ 数据库连接失败!")
        print(f"错误信息: {str(e)}")
        
        # 提供一些常见问题的解决建议
        print("\n可能的解决方案:")
        print("1. 检查SQL Server服务是否正在运行")
        print("2. 确认数据库名称、用户名和密码是否正确")
        print("3. 检查防火墙设置，确保端口1433开放")
        print("4. 确认SQL Server身份验证模式已启用")
        print("5. 安装ODBC Driver 17 for SQL Server")
        
        return False
        
    except Exception as e:
        print("❌ 发生未知错误!")
        print(f"错误信息: {str(e)}")
        return False

def check_dependencies():
    """检查所需的依赖包"""
    try:
        import pyodbc
        print("✅ pyodbc 模块已安装")
    except ImportError:
        print("❌ pyodbc 模块未安装")
        print("请运行: pip install pyodbc")
        return False
    
    # 检查可用的ODBC驱动
    try:
        drivers = pyodbc.drivers()
        print(f"可用的ODBC驱动: {drivers}")
        
        sql_server_drivers = [d for d in drivers if 'SQL Server' in d]
        if sql_server_drivers:
            print(f"✅ 找到SQL Server驱动: {sql_server_drivers}")
        else:
            print("❌ 未找到SQL Server ODBC驱动")
            print("请安装 Microsoft ODBC Driver for SQL Server")
            
    except Exception as e:
        print(f"检查驱动时出错: {e}")
    
    return True

if __name__ == "__main__":
    print("SQL Server 数据库连接测试程序")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # 测试连接
    success = test_sqlserver_connection()
    
    if success:
        print("\n🎉 测试完成 - 连接成功!")
    else:
        print("\n💥 测试完成 - 连接失败!")
        sys.exit(1)