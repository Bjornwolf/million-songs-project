EXAMPLE_GRAPH = {
    "a": {
        "track_id": "a",
        "similars": [
            ["b", 0.99],
            ["c", 0.12],
            ["d", 0.5]
        ],
        "tags": [
            ["black metal", 90],
            ["metal", 80],
            ["rock", 20]
        ]
    },
    "b": {
        "track_id": "b",
        "similars": [
            ["a", 0.99],
            ["d", 0.12]
        ],
        "tags": [
            ["rock", 60],
            ["jazz", 40]
        ],
    },
    "c": {
        "track_id": "c",
        "similars": [
          ["a", 0.12]
        ],
        "tags": []
    },
    "d": {
        "track_id": "d",
        "similars": [
          ["a", 0.5],
          ["b", 0.12]
        ],
        "tags": [
            ["jazz", 99],
            ["fusion", 70]
        ]
    }
}
