# Module to export data from dataplatform to a csv file to train the model
# uses the export query in data/sql/data_export.sql
import csv
import logging
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from sqlalchemy import text

from noshow.config import setup_root_logger
from noshow.database.connection import get_connection_string, get_engine

load_dotenv(override=True)

logger = logging.getLogger(__name__)
console = Console()


def export_data(
    db_host: str = "dataplatform",
    db_database: str = "PUB",
    output_path: str = "poliafspraken_no_show.csv",
    batch_size: int = 10_000,
):
    """Function to efficiently export data from the dataplatform to a csv file

    Used to export data to train the model. The data is exported in batches to
    avoid memory issues.

    Parameters
    ----------
    db_host : str, optional
        hostname of the database server, by default "dataplatform"
    db_database : str, optional
        Name of the database, by default "PUB"
    output_path : str, optional
        Name of the output file, located in the data/raw folder,
        by default "poliafspraken_no_show.csv"
    batch_size : int, optional
        batch size for reading from query result and writing to csv, by default 1000
    """
    connection_string, _ = get_connection_string(
        db_database=db_database, db_host=db_host
    )
    with open(Path(__file__).parents[3] / "data/sql/data_export.sql") as f:
        sql_query = f.read()

    output_csv = Path(__file__).parents[3] / "data/raw" / output_path

    db_engine = get_engine(connection_string)
    with db_engine.connect() as conn:
        logger.info("Executing export query...")
        with console.status("[bold green]Executing export query..."):
            result = conn.execution_options(stream_results=True).execute(
                text(sql_query)
            )
        logger.info("Export query executed successfully")

        with console.status("[bold green]Exporting data to CSV..."):
            with open(output_csv, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)

                # Write the header row
                writer.writerow(result.keys())

                # Write data in batches
                while True:
                    rows = result.fetchmany(batch_size)
                    if not rows:
                        break
                    writer.writerows(rows)

    logger.info(f"Data exported to {output_csv}")


if __name__ == "__main__":
    setup_root_logger()
    export_data()
