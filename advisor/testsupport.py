from datetime import datetime, timezone


def synthetic_models(count=25):
    now = datetime.now(timezone.utc).timestamp()
    models = []
    for i in range(count):
        quality = 90 - i
        models.append({
            'id': f'vendor/m{i}', 'canonical_slug': f'vendor/m{i}', 'name': f'M{i}', 'created': now,
            'pricing': {'prompt': str((i + 1) / 1_000_000), 'completion': str((i + 1) / 1_000_000)},
            'benchmarks': {'artificial_analysis': {'intelligence_index': quality, 'coding_index': quality, 'agentic_index': quality}, 'design_arena': []},
            'architecture': {'output_modalities': ['text']},
            'supported_parameters': ['tools'], 'context_length': 200000,
        })
    return models


if __name__ == '__main__':
    import json
    print(json.dumps(synthetic_models(), ensure_ascii=False))


# This module exists only to keep deterministic unit fixtures out of production code.
