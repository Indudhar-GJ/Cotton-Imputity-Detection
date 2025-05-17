import sqlite3

def create_table(conn):
    """Create a table with all your specified parameters"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS params (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                -- Boolean parameters
                AcquisitionLineRateEnable BOOLEAN,
                ReverseX BOOLEAN,
                GammaEnable BOOLEAN,
                HueEnable BOOLEAN,
                SaturationEnable BOOLEAN,
                
                -- Hex parameter (stored as INTEGER)
                PixelFormat INTEGER,
                
                -- Integer parameters
                Exposure INTEGER,
                AcquisitionLineRate INTEGER,
                AutoExposureTimeLowerLimit INTEGER,
                AutoExposureTimeUpperLimit INTEGER,
                Width INTEGER,
                Height INTEGER,
                BalanceWhiteAuto INTEGER,
                
                -- Additional parameters
                ModelPath TEXT,
                DatasetPath TEXT,
                Epochs INTEGER,
                
                -- Metadata
                CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                LastModified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create a trigger to update LastModified timestamp on updates
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS update_params_timestamp
            AFTER UPDATE ON params
            BEGIN
                UPDATE  params
                SET LastModified = CURRENT_TIMESTAMP
                WHERE id = old.id;
            END;
        """)
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")

if __name__=="__main__":
    conn = sqlite3.connect('config.db')
    create_table(conn)