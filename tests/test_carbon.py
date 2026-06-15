import pandas as pd
import pytest

from carbon_portfolio.carbon import (
    carbon_snapshot_as_of,
    load_carbon_intensity,
)


def test_load_carbon_intensity_validates_calculation(tmp_path):
    path = tmp_path / "carbon.csv"
    pd.DataFrame(
        {
            "ticker": ["A"],
            "reporting_year": [2022],
            "available_date": ["2023-07-01"],
            "scope1_tco2e": [60.0],
            "scope2_location_tco2e": [40.0],
            "revenue_usd_mn": [20.0],
            "carbon_intensity_tco2e_per_usd_mn": [5.0],
        }
    ).to_csv(path, index=False)

    panel = load_carbon_intensity(path, ["A"])
    assert panel.loc[0, "carbon_intensity_tco2e_per_usd_mn"] == 5.0


def test_snapshot_uses_only_information_available_as_of_date():
    panel = pd.DataFrame(
        {
            "ticker": ["A", "A", "B"],
            "reporting_year": [2021, 2022, 2021],
            "available_date": pd.to_datetime(
                ["2022-07-01", "2023-07-01", "2022-08-01"]
            ),
            "carbon_intensity_tco2e_per_usd_mn": [10.0, 8.0, 20.0],
        }
    )
    snapshot = carbon_snapshot_as_of(panel, "2022-12-31", ["A", "B"])
    assert snapshot.loc["A", "reporting_year"] == 2021
    assert snapshot.loc["B", "reporting_year"] == 2021


def test_snapshot_reports_missing_point_in_time_coverage():
    panel = pd.DataFrame(
        {
            "ticker": ["A"],
            "reporting_year": [2022],
            "available_date": pd.to_datetime(["2023-07-01"]),
            "carbon_intensity_tco2e_per_usd_mn": [8.0],
        }
    )
    with pytest.raises(ValueError, match="No point-in-time"):
        carbon_snapshot_as_of(panel, "2022-12-31", ["A"])
