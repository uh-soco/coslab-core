def identity_comparator( tag1, tag2 ):
    if tag1 == tag2:
        return 1
    else:
        return 0

def compare_tags( results, service1, service2, comparator = identity_comparator ):

    images = results.labels ## dict of dicts

    for image in images:
        tags1 = image[ service1 ]
        tags2 = image[ service2 ]

        best_similarities = {}
        for tag1 in tags1:
            similarities = []
            for tag2 in tags2:
                similarity = comparator( tag1, tag2 )
                similarities.append( similarity )
            best_similarities[ tag1 ] = max( similarities )
            
    return best_similarities
