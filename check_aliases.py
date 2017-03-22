def check_aliases_posting(aliases, entry, posting):
    for alias in aliases:
        if hasattr(posting, 'meta') and posting.meta and alias in posting.meta:
            return posting.meta[alias]
        if hasattr(entry, 'meta') and entry.meta and alias in entry.meta:
            return entry.meta[alias]
        if hasattr(entry, 'tags') and hasattr(entry.tags, alias):
            return ''
    return False

def check_aliases_entry(aliases, entry, seperator):
    for alias in aliases:
        if hasattr(entry, 'meta') and entry.meta and alias in entry.meta:
            return entry.meta[alias]
        if hasattr(entry, 'tags') and entry.tags:
            for tag in entry.tags:
                if tag[0:len(alias+seperator)] == alias+seperator:
                    return tag[len(alias+seperator):]
    return False

