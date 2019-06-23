"""
Author(s):      Carson Schubert (carson.schubert14@gmail.com)
Date Created:   05/03/2019

Provides useful helper functions for plugins.
"""

from datetime import datetime
from ravenml.data.interfaces import Dataset
from ravenml.utils.question import user_input

def fill_basic_metadata(metadata: dict, dataset: Dataset):
    """Adds basic metadata to the provided dictionary.

    Args:
        metadata (dict): metadata dictionary object
        dataset (Dataset): training dataset
    
    Example:
        >>> metadata = {}
        >>> fill_basic_metadata(metadata, dataset)
    """
    metadata['created_by'] = user_input('Please enter your first and last name:')
    metadata['comments'] = user_input('Please enter any comments about this training:')
    metadata['date_started_at'] = datetime.utcnow().isoformat() + "Z"
    metadata['dataset_used'] = dataset.metadata
