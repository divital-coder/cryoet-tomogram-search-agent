# src/toolkits/tomogram_toolkit.py
# src/toolkits/tomogram_toolkit.py
from camel.toolkits import BaseToolkit
from typing import List, Dict, Any
import cryoet_data_portal as portal
from pathlib import Path

class TomogramToolkit(BaseToolkit):
    """Toolkit for CryoET data portal interactions"""
    
    def __init__(self):
        super().__init__()
        self.client = portal.Client()
        self.output_dir = Path("./results")
        self.output_dir.mkdir(exist_ok=True)

    def search_datasets(self, protein_type: str, resolution: str) -> Dict[str, Any]:
        """
        Search for datasets based on protein type and resolution.
        
        Args:
            protein_type (str): Type of protein to search for
            resolution (str): Resolution range (e.g., '0-5')
            
        Returns:
            Dict[str, Any]: Search results
        """
        try:
            # Convert resolution range to float values
            min_res, max_res = map(float, resolution.split('-'))
            
            # Build search criteria
            criteria = [
                portal.Dataset.name.ilike(f"%{protein_type}%"),
                portal.Dataset.runs.tomograms.voxel_spacing.x >= min_res,
                portal.Dataset.runs.tomograms.voxel_spacing.x <= max_res
            ]
            
            # Execute search
            datasets = portal.Dataset.find(self.client, criteria)
            
            # Format results
            results = []
            for dataset in datasets:
                results.append({
                    "id": dataset.id,
                    "name": dataset.name,
                    "description": dataset.description,
                    "authors": dataset.authors,
                    "release_date": str(dataset.release_date),
                    "runs_count": len(dataset.runs)
                })
            
            return {
                "status": "success",
                "count": len(results),
                "datasets": results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def get_dataset_details(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific dataset.
        
        Args:
            dataset_id (str): ID of the dataset
            
        Returns:
            Dict[str, Any]: Dataset details
        """
        try:
            dataset = portal.Dataset.get_by_id(self.client, dataset_id)
            
            # Get tomogram information
            tomograms = []
            for run in dataset.runs:
                for tomogram in run.tomograms:
                    tomograms.append({
                        "id": tomogram.id,
                        "name": tomogram.name,
                        "voxel_spacing": {
                            "x": tomogram.voxel_spacing.x,
                            "y": tomogram.voxel_spacing.y,
                            "z": tomogram.voxel_spacing.z
                        }
                    })
            
            return {
                "status": "success",
                "dataset": {
                    "id": dataset.id,
                    "name": dataset.name,
                    "description": dataset.description,
                    "authors": dataset.authors,
                    "release_date": str(dataset.release_date),
                    "tomograms": tomograms
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def download_tomogram(self, dataset_id: str, tomogram_id: str) -> Dict[str, Any]:
        """
        Download a specific tomogram.
        
        Args:
            dataset_id (str): ID of the dataset
            tomogram_id (str): ID of the tomogram
            
        Returns:
            Dict[str, Any]: Download status and information
        """
        try:
            dataset = portal.Dataset.get_by_id(self.client, dataset_id)
            
            # Find the specific tomogram
            target_tomogram = None
            for run in dataset.runs:
                for tomogram in run.tomograms:
                    if tomogram.id == tomogram_id:
                        target_tomogram = tomogram
                        break
                if target_tomogram:
                    break
            
            if not target_tomogram:
                raise ValueError(f"Tomogram {tomogram_id} not found in dataset {dataset_id}")
            
            # Download the tomogram
            output_path = self.output_dir / f"tomogram_{tomogram_id}.mrc"
            target_tomogram.download_mrcfile(output_path)
            
            return {
                "status": "success",
                "message": f"Downloaded tomogram to {output_path}",
                "file_path": str(output_path)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def get_tools(self) -> List[callable]:
        """Get all tools in the toolkit"""
        return [
            self.search_datasets,
            self.get_dataset_details,
            self.download_tomogram
        ]

