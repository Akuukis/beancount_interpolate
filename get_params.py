def get_params(aliases, entry, posting):
    for alias in aliases:
        if hasattr(posting, 'meta') and posting.meta and alias in posting.meta:
            return posting.meta[alias]
        if hasattr(entry, 'meta') and entry.meta and alias in entry.meta:
            return entry.meta[alias]
        if hasattr(entry, 'tags') and hasattr(entry.tags, alias):
            return ''
    return False
