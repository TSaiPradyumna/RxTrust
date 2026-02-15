from app.nsq_registry import NSQRegistry


def test_exact_match_found_for_known_batch_and_manufacturer():
    registry = NSQRegistry(dataset_path="data/cdsco_nsq_dec25_subset.json")
    row = registry.find_exact_match("TS-249", "Trimedix Pharma (P) Ltd.")
    assert row is not None
    assert row["id"] == 58
