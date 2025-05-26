def jaccard_distance(set1, set2):
    # Symmetric difference of two sets
    symmetric_difference = set1.symmetric_difference(set2)
    # Unions of two sets
    union = set1.union(set2)
    #print(len(union), len(symmetric_difference))

    return float(len(union))/float(len(symmetric_difference))

if __name__ == "__main__":
    # Example usage
    set1 = {"apple", "banana", "cherry"}
    set2 = {"banana", "cherry", "date"}
    print(jaccard_distance(set1, set2))