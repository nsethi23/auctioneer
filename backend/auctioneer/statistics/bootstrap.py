import random


def bootstrap_mean_confidence_interval(
    values,
    num_resamples=1000,
    confidence=0.95,
    rng=None,
):
    if not values:
        raise ValueError("values must not be empty")

    if num_resamples <= 0:
        raise ValueError("num_resamples must be positive")

    if confidence <= 0 or confidence >= 1:
        raise ValueError("confidence must be between 0 and 1")

    if rng is None:
        rng = random.Random()

    mean = sum(values) / len(values)
    bootstrap_means = []

    for _ in range(num_resamples):
        sample = []

        # Sample with replacement to simulate another possible auction dataset.
        for _ in range(len(values)):
            sample.append(rng.choice(values))

        sample_mean = sum(sample) / len(sample)
        bootstrap_means.append(sample_mean)

    # Percentile bounds come from the empirical distribution of resampled means.
    bootstrap_means.sort()

    lower_percentile = (1 - confidence) / 2
    upper_percentile = 1 - lower_percentile

    lower_index = int(lower_percentile * (num_resamples - 1))
    upper_index = int(upper_percentile * (num_resamples - 1))

    return {
        "mean": mean,
        "lower": bootstrap_means[lower_index],
        "upper": bootstrap_means[upper_index],
        "confidence": confidence,
        "num_resamples": num_resamples,
    }
