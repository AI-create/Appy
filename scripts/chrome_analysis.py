import sqlite3
from androguard.core.bytecodes.apk import APK
import datetime

# SQLite Database Setup
DB_NAME = "apk_metadata.db"

def create_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Create a table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS apk_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    package_name TEXT,
                    version TEXT,
                    permissions TEXT,
                    activities TEXT,
                    services TEXT,
                    receivers TEXT,
                    providers TEXT,
                    files TEXT,
                    timestamp TEXT
                )''')
    conn.commit()
    conn.close()

def save_to_db(metadata):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Insert metadata into the table
    c.execute('''INSERT INTO apk_metadata (
                    package_name, version, permissions, activities, services,
                    receivers, providers, files, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                    metadata['package_name'],
                    metadata['version'],
                    ', '.join(metadata['permissions']),
                    ', '.join(metadata['activities']),
                    ', '.join(metadata['services']),
                    ', '.join(metadata['receivers']),
                    ', '.join(metadata['providers']),
                    ', '.join(metadata['files']),
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))

    conn.commit()
    conn.close()
    print(f"Metadata for {metadata['package_name']} saved to the database.")

# APK Analyzer class
class APKAnalyzer:
    def __init__(self, apk_path):
        self.apk_path = apk_path
        self.apk = APK(self.apk_path)

    def get_package_name(self):
        return self.apk.get_package()

    def get_version(self):
        return self.apk.get_androidversion_name()

    def get_permissions(self):
        return self.apk.get_permissions()

    def get_activities(self):
        return self.apk.get_activities()

    def get_services(self):
        return self.apk.get_services()

    def get_receivers(self):
        return self.apk.get_receivers()

    def get_providers(self):
        return self.apk.get_providers()

    def get_files(self):
        return self.apk.get_files()

    def get_metadata(self):
        return {
            "package_name": self.get_package_name(),
            "version": self.get_version(),
            "permissions": self.get_permissions(),
            "activities": self.get_activities(),
            "services": self.get_services(),
            "receivers": self.get_receivers(),
            "providers": self.get_providers(),
            "files": self.get_files(),
        }

# Example usage:
if __name__ == "__main__":
    apk_path = r'C:\Appy\scripts\Chrome.apk'  
    analyzer = APKAnalyzer(apk_path)

    # Create the database and table if it doesn't exist
    create_db()

    # Extract metadata
    metadata = analyzer.get_metadata()

    # Save metadata to the database
    save_to_db(metadata)

    # Print the collected metadata
    print("APK Metadata:")
    print(f"Package Name: {metadata['package_name']}")
    print(f"Version: {metadata['version']}")
    print(f"Permissions: {', '.join(metadata['permissions'])}")
    print(f"Activities: {', '.join(metadata['activities'])}")
    print(f"Services: {', '.join(metadata['services'])}")
    print(f"Receivers: {', '.join(metadata['receivers'])}")
    print(f"Providers: {', '.join(metadata['providers'])}")
    print(f"Files: {', '.join(metadata['files'])}")
