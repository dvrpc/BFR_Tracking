import pandas as pd
import env_vars as ev
from env_vars import ENGINE
from pathlib import Path


def main():
    data_folder = Path(ev.DATA_ROOT)
    interim_csvs = data_folder / "paving_package/CSVs"

    for filepath in interim_csvs.rglob("*.csv"):
        print(filepath.stem)
        df = pd.read_csv(filepath)
        df.to_sql(fr"{filepath.stem}", con=ENGINE, if_exists="replace")


if __name__ == "__main__":
    main()
