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
                
                -- Hex parameter 
                PixelFormat INTEGER,
                
                -- Integer parameters
                ExposureAuto INTEGER,
                AcquisitionLineRate INTEGER,
                AutoExposureTimeLowerLimit INTEGER,
                AutoExposureTimeUpperLimit INTEGER,
                Width INTEGER,
                Height INTEGER,
                BalanceWhiteAuto INTEGER,
                GammaSelector INTEGER,
                
                -- Additional parameters
                ModelPath TEXT,
                ScriptPath TEXT DEFAULT './GUI_savetofolder.py',
                DatasetPath TEXT,
                TrainingPath TEXT DEFAULT './train.py',
                Epochs INTEGER,
                       
                -- Confidence Scores
                Cloth INTEGER,
                Thread INTEGER, 
                Jute INTEGER,
                Packet INTEGER,
                NewContaminant INTEGER,
                       
                -- Count
                steps INTEGER DEFAULT 1,
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
    conn = sqlite3.connect('config1.db')
    create_table(conn)