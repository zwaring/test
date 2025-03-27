from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
import os
import pycdlib
import humanize

app = FastAPI(
    title="ISO Files API",
    description="API for querying ISO file information",
    version="1.0.0"
)

class ISOFile(BaseModel):
    id: int
    name: str
    size_mb: float
    size_human: str
    created_date: str
    modified_date: str
    path: str
    volume_label: Optional[str] = None
    file_system: Optional[str] = None
    is_valid_iso: bool = False
    iso_creation_date: Optional[str] = None
    iso_modification_date: Optional[str] = None
    iso_application_id: Optional[str] = None
    iso_publisher_id: Optional[str] = None
    iso_preparer_id: Optional[str] = None

def get_iso_metadata(iso_path: Path) -> Dict:
    """Extract metadata from ISO file using pycdlib"""
    metadata = {
        'volume_label': None,
        'file_system': None,
        'is_valid_iso': False,
        'iso_creation_date': None,
        'iso_modification_date': None,
        'iso_application_id': None,
        'iso_publisher_id': None,
        'iso_preparer_id': None
    }
    
    try:
        iso = pycdlib.PyCdlib()
        iso.open(str(iso_path))
        
        # Get primary volume descriptor
        metadata['is_valid_iso'] = True
        metadata['volume_label'] = iso.pvd.volume_identifier.decode('utf-8').strip()
        metadata['file_system'] = 'ISO9660'
        
        # Get dates
        metadata['iso_creation_date'] = datetime.strptime(
            iso.pvd.volume_creation_date.decode('utf-8'), 
            "%Y%m%d%H%M%S00"
        ).isoformat()
        metadata['iso_modification_date'] = datetime.strptime(
            iso.pvd.volume_modification_date.decode('utf-8'),
            "%Y%m%d%H%M%S00"
        ).isoformat()
        
        # Get additional identifiers
        metadata['iso_application_id'] = iso.pvd.application_identifier.decode('utf-8').strip()
        metadata['iso_publisher_id'] = iso.pvd.publisher_identifier.decode('utf-8').strip()
        metadata['iso_preparer_id'] = iso.pvd.preparer_identifier.decode('utf-8').strip()
        
        iso.close()
    except Exception as e:
        print(f"Error reading ISO metadata: {str(e)}")
    
    return metadata

def get_iso_files(directory: str = None) -> List[ISOFile]:
    """Get list of ISO files from the specified directory"""
    if directory is None:
        directory = os.getenv("ISO_DIR", "/isofiles")
    
    iso_files = []
    iso_path = Path(directory)
    
    if not iso_path.exists():
        return []
    
    for idx, iso_file in enumerate(iso_path.glob("*.iso"), 1):
        stats = iso_file.stat()
        size_bytes = stats.st_size
        size_mb = round(size_bytes / (1024 * 1024), 2)
        
        # Get ISO metadata
        metadata = get_iso_metadata(iso_file)
        
        iso_files.append(ISOFile(
            id=idx,
            name=iso_file.name,
            size_mb=size_mb,
            size_human=humanize.naturalsize(size_bytes),
            created_date=datetime.fromtimestamp(stats.st_ctime).isoformat(),
            modified_date=datetime.fromtimestamp(stats.st_mtime).isoformat(),
            path=str(iso_file),
            **metadata
        ))
    
    return iso_files

@app.get("/")
async def root():
    return {"message": "Welcome to the ISO Files API"}

@app.get("/isos", response_model=List[ISOFile])
async def list_isos():
    """
    Get a list of all ISO files with detailed metadata
    """
    files = get_iso_files()
    return files

@app.get("/isos/search/", response_model=List[ISOFile])
async def search_isos(
    name: Optional[str] = Query(None, description="Search by file name"),
    min_size: Optional[float] = Query(None, description="Minimum size in MB"),
    max_size: Optional[float] = Query(None, description="Maximum size in MB"),
    volume_label: Optional[str] = Query(None, description="Search by volume label")
):
    """
    Search ISO files by name, size range, or volume label
    """
    files = get_iso_files()
    
    if name:
        files = [f for f in files if name.lower() in f.name.lower()]
    if min_size is not None:
        files = [f for f in files if f.size_mb >= min_size]
    if max_size is not None:
        files = [f for f in files if f.size_mb <= max_size]
    if volume_label:
        files = [f for f in files if f.volume_label and volume_label.lower() in f.volume_label.lower()]
    
    return files

@app.get("/isos/{iso_id}", response_model=ISOFile)
async def get_iso(iso_id: int):
    """
    Get detailed information about a specific ISO file by ID
    """
    files = get_iso_files()
    if 0 < iso_id <= len(files):
        return files[iso_id - 1]
    raise HTTPException(status_code=404, detail="ISO file not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 