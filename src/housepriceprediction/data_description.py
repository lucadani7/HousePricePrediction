from pathlib import Path


class DataDescription:
    """Parses and manages feature metadata and missing value rules
    from the project's text-based data description file.
    """

    def __init__(self, file_path: Path) -> None:
        self._file_path: Path = file_path
        self._features: dict[str, dict[str, str]] = {}
        self._parse()

    def _parse(self) -> None:
        """Parses the text file line by line using current_feature tracking
        and builds a single source of truth dictionary mapping features to their codes.
        """
        raw_text = self._file_path.read_text(encoding="utf-8")
        current_feature: str | None = None
        feature_lines: dict[str, list[str]] = {}

        for line in raw_text.splitlines():
            if line and not line.startswith(" ") and not line.startswith("\t"):
                if ":" in line:
                    current_feature = line.split(":")[0].strip()
                    feature_lines[current_feature] = []
                else:
                    current_feature = None
            elif current_feature and line.strip():
                feature_lines[current_feature].append(line.strip())

        for feature, lines in feature_lines.items():
            code_dict: dict[str, str] = {}
            for line in lines:
                parts = line.replace("\t", ":").split(":", 1)
                code = parts[0].strip()
                desc = parts[1].strip() if len(parts) > 1 else ""
                code_dict[code] = desc
            self._features[feature] = code_dict

    @property
    def columns_where_na_means_absent(self) -> tuple[str, ...]:
        """Returns an immutable, sorted tuple of categorical columns
        where missing values (NA) structurally mean 'None' / absence.
        """
        na_cols = [
            feat for feat, code_dict in self._features.items() if "NA" in code_dict
        ]
        return tuple(sorted(na_cols))

    def has_codes(self, column: str) -> bool:
        """Checks whether a given column has listed codes in the data description.
        Args:
            column (str): The name of the feature.
        Returns:
            bool: True if the column exists and has listed codes, False otherwise.
        """
        return bool(self._features.get(column))

    def codes(self, column: str) -> dict[str, str]:
        """Returns a dictionary mapping category codes to their descriptions
        for a specific column (protecting internal state by returning a copy).
        Args:
            column (str): The name of the feature.
        Returns:
            dict[str, str]: A dictionary of codes and their descriptions.
        Raises:
            KeyError: If the column does not exist in the data description file.
            ValueError: If the column exists but has no listed codes.
        """
        if column not in self._features:
            raise KeyError(
                f"Column '{column}' was not found in the data description file."
            )

        code_dict = self._features[column]
        if not code_dict:
            raise ValueError(
                f"Column '{column}' has no listed codes in data_description.txt"
            )

        return dict(code_dict)
