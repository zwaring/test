import os
import json
from datetime import datetime
from pathlib import Path
import sys

def get_iso_info(directory):
    iso_files = []
    iso_path = Path(directory)
    
    if not iso_path.exists():
        print(f"Error: Directory {directory} does not exist")
        return {'items': []}
    
    try:
        # Get all ISO files in the directory
        iso_files_list = list(iso_path.glob('*.iso'))
        print(f"Found {len(iso_files_list)} ISO files in {directory}")
        
        for iso_file in iso_files_list:
            try:
                file_info = {
                    'id': len(iso_files) + 1,
                    'name': iso_file.name,
                    'description': f"ISO file: {iso_file.name}",
                    'category': 'ISO',
                    'size_mb': round(iso_file.stat().st_size / (1024 * 1024), 2),
                    'created_date': datetime.fromtimestamp(iso_file.stat().st_ctime).isoformat(),
                    'modified_date': datetime.fromtimestamp(iso_file.stat().st_mtime).isoformat(),
                    'path': str(iso_file)
                }
                iso_files.append(file_info)
                print(f"Processed: {iso_file.name}")
            except Exception as e:
                print(f"Error processing {iso_file.name}: {str(e)}")
                continue
                
    except Exception as e:
        print(f"Error accessing directory {directory}: {str(e)}")
    
    return {'items': iso_files}

def main():
    # Use the mounted directory path inside the container
    iso_directory = '/isofiles'
    
    try:
        # Get ISO file information
        data = get_iso_info(iso_directory)
        
        # Write to JSON file in the mounted volume so it's accessible from host
        output_file = '/isofiles/data.json'
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)
            
        print(f"\nSuccessfully processed {len(data['items'])} ISO files")
        print(f"Data has been written to {output_file}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 