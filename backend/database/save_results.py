import sqlite3
import json

from datetime import datetime
from pathlib import Path
from dataclasses import asdict, is_dataclass

DB_NAME = Path(__file__).resolve().parent / "geosentinel.db"


def _to_db_path(value):
    """
    Convert pathlib.Path objects to strings.
    """

    if value is None:
        return None

    if isinstance(value, Path):
        return str(value)

    return str(value)


def _make_json_serializable(obj):
    """
    Recursively convert dataclasses and nested objects
    into JSON-serializable dictionaries/lists.
    """

    if is_dataclass(obj):
        return {
            key: _make_json_serializable(value)
            for key, value in asdict(obj).items()
        }

    if isinstance(obj, dict):
        return {
            key: _make_json_serializable(value)
            for key, value in obj.items()
        }

    if isinstance(obj, list):
        return [
            _make_json_serializable(item)
            for item in obj
        ]

    if isinstance(obj, tuple):
        return [
            _make_json_serializable(item)
            for item in obj
        ]

    return obj


def save_result(

    analysis_name,

    aoi_id,
    aoi_name,

    objects_detected,

    confidence_score,
    change_percentage,

    segformer_results,

    dynamic_world_results,
    dynamic_world_transition_results,

    fusion_results,
    transition_results,

    geospatial_results,

    evidence_results,

    historical_results,

    report,

    analysis_directory,

    before_image_path=None,
    after_image_path=None,

    prithvi_before_path=None,
    prithvi_after_path=None,

    segmask_before_path=None,
    segmask_after_path=None,

    changestar_result_path=None,

    dynamic_world_before_path=None,
    dynamic_world_after_path=None,
    dynamic_world_transition_map=None,

    grounding_dino_before_path=None,
    grounding_dino_after_path=None,

    change_map_path=None,
    change_binary_path=None,

    execution_time=0.0,

    pipeline_version="GeoSentinel AI v1.0",
):
    """
    Save one complete GeoSentinel AI analysis.
    """

    conn = None

    try:

        conn = sqlite3.connect(DB_NAME)

        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO analysis_results
            (

                analysis_name,

                timestamp,

                aoi_id,
                aoi_name,

                confidence_score,
                change_percentage,

                objects_detected,

                prithvi_results,

                dynamic_world_results,
                dynamic_world_transition_results,

                fusion_results,
                transition_results,

                geospatial_results,

                evidence_results,

                historical_results,

                report,

                pipeline_version,
                execution_time,

                analysis_directory,

                before_image_path,
                after_image_path,

                prithvi_before_path,
                prithvi_after_path,

                segmask_before_path,
                segmask_after_path,

                changestar_result_path,

                dynamic_world_before_path,
                dynamic_world_after_path,

                dynamic_world_transition_map,

                grounding_dino_before_path,
                grounding_dino_after_path,

                change_map_path,
                change_binary_path

            )

            VALUES
            (

                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?

            )
            """,

            (

                analysis_name,

                datetime.now().isoformat(),

                aoi_id,
                aoi_name,

                confidence_score,
                change_percentage,

                json.dumps(
                    _make_json_serializable(objects_detected)
                ),

                json.dumps(
                    _make_json_serializable(segformer_results)
                ),

                json.dumps(
                    _make_json_serializable(dynamic_world_results)
                ),

                json.dumps(
                    _make_json_serializable(
                        dynamic_world_transition_results
                    )
                ),

                json.dumps(
                    _make_json_serializable(fusion_results)
                ),

                json.dumps(
                    _make_json_serializable(transition_results)
                ),

                json.dumps(
                    _make_json_serializable(geospatial_results)
                ),

                json.dumps(
                    _make_json_serializable(
                        evidence_results
                    )
                ),

                json.dumps(
                    _make_json_serializable(
                        historical_results
                    )
                ),

                report,

                pipeline_version,
                execution_time,

                _to_db_path(analysis_directory),

                _to_db_path(before_image_path),
                _to_db_path(after_image_path),

                _to_db_path(prithvi_before_path),
                _to_db_path(prithvi_after_path),

                _to_db_path(segmask_before_path),
                _to_db_path(segmask_after_path),

                _to_db_path(changestar_result_path),

                _to_db_path(dynamic_world_before_path),
                _to_db_path(dynamic_world_after_path),

                _to_db_path(dynamic_world_transition_map),

                _to_db_path(grounding_dino_before_path),
                _to_db_path(grounding_dino_after_path),

                _to_db_path(change_map_path),
                _to_db_path(change_binary_path),

            ),

        )

        conn.commit()

        print(
            f"\nAnalysis successfully saved for {aoi_name} ({aoi_id})"
        )

    except Exception as e:

        print(f"\nDatabase Error: {e}")
        raise

    finally:

        if conn is not None:
            conn.close()