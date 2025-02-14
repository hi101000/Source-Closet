def jaccard_distance(set1, set2):
    # Symmetric difference of two sets
    symmetric_difference = set1.symmetric_difference(set2)
    # Unions of two sets
    union = set1.union(set2)

    return float(len(union))/float(len(symmetric_difference))