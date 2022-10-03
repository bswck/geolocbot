from __future__ import annotations

import collections
import typing

import pandas as pd

if typing.TYPE_CHECKING:
    from typing import Any

    from geolocbot.scraper import Subdivisions


TERYT = collections.namedtuple("TERYT", "sub terc simc nts")


class TERCBase:
    powiat_rights: str | None
    wd_prop: str = "P1653"

    def get_wd_key(self, primary: bool = True) -> str | None:
        if primary and self.powiat_rights:
            return self.code(pow_level=True)
        return self.code()

    def code(self, pow_level: bool = False) -> str | None:
        raise NotImplementedError


class TERC(
    TERCBase,
    collections.namedtuple(
        "TERC",
        "sub woj pow gmi rodz powiat_rights",
        defaults=[None, None, None, None, None, None],
    ),
):
    registry_name: str = "TERC"

    def code(self, pow_level: bool = False) -> str | None:
        code = None
        if self.woj and not pow_level or self.powiat_rights:
            code = (
                self.woj
                + (self.powiat_rights if pow_level else self.pow)
                + ((self.gmi + self.rodz) if self.gmi and not pow_level else "")
            )
        return code


class SIMC(
    collections.namedtuple(
        "SIMC",
        "sub sym sympod rm rm_nazwa",
        defaults=[None, None, None, None, None],
    )
):
    registry_name: str = "SIMC"
    wd_prop: str = "P4046"

    def get_wd_key(self, _primary: bool = True) -> str | None:
        return self.sym


class NTS(
    TERCBase,
    collections.namedtuple(
        "NTS",
        "sub poziom region woj podreg pow gmi rodz powiat_rights",
        defaults=[None, None, None, None, None, None, None, None, None],
    ),
):
    registry_name: str = "NTS"

    def code(self, pow_level: bool = False) -> str | None:
        code = None
        if self.woj and not pow_level or self.powiat_rights:
            # There is no POZIOM column in Wikidata mess
            code = self.region
            code += (
                self.woj
                + self.podreg
                + (self.powiat_rights if pow_level else self.pow)
                + ((self.gmi + self.rodz) if self.gmi and not pow_level else "")
            )
        return code


class TERYTSearch:
    NAZWA_DOD_RELEVANCE: dict[str, int] = {
        "obszar wiejski": 0,
        "gmina wiejska": 0,
        "gmina miejsko-wiejska": 1,
        "gmina miejska": 2,
        "delegatura": 3,
        "dzielnica": 3,
        "miasto": 4,
        "miasto na prawach powiatu": 5,
        "gmina miejska, miasto stołeczne": 6,
        "miasto stołeczne, na prawach powiatu": 7,
        "powiat": 8,
        "województwo": 9,
    }

    RODZ_RELEVANCE: dict[str, int] = {
        "5": 0,  # obszary wiejskie w gminach miejsko-wiejskich
        "2": 1,  # gminy wiejskie
        "3": 1,  # gminy miejsko-wiejskie
        "9": 2,  # delegatury
        "8": 2,  # dzielnice
        "1": 3,  # gminy miejskie
        "4": 4,  # miasta w gminach miejsko-wiejskich
    }

    WMRODZ_RELEVANCE: dict[str, int] = {
        "03": 0,  # przysiółek
        "05": 0,  # osada leśna
        "02": 1,  # kolonia
        "06": 1,  # osiedle
        "00": 2,  # część
        "04": 3,  # osada
        "01": 4,  # wieś
        "07": 5,  # schronisko turystyczne
        "99": 6,  # część miasta
        "98": 7,  # delegatura
        "95": 7,  # dzielnica
        "96": 8,  # miasto
    }

    POWIAT_CITY_NAZWA_DOD: str = "na prawach powiatu"

    def __init__(self) -> None:
        self._data: dict[str, pd.DataFrame] = {}
        self._rm: dict[str, str] = {}

    def load_registry(
        self, code: str, filename: str, fmt: str = "csv", **kwargs: Any
    ) -> None:
        """Load registry data (TERC, SIMC, NTS, WMRODZ) from a file and cache it."""
        if fmt == "csv":
            df = pd.read_csv(filename, dtype="object", **kwargs)
        elif fmt == "xml":
            df = pd.read_xml(filename, **kwargs)
        else:
            raise ValueError(f"unrecognized TERYT registry dataset format: .{fmt}")
        self._data[code] = df

    def get_registry(self, code: str) -> pd.DataFrame:
        """Get registry data (TERC, SIMC, NTS, WMRODZ) as a pandas DataFrame."""
        try:
            return self._data[code]
        except KeyError as exc:
            raise ValueError(f"{code} registry was not loaded") from exc

    def memoize_rm(self) -> None:
        """
        Cache data from the WMRODZ dataset.

        WMRODZ is a suplementary dataset to SIMC. It contains a mapping between
        the RM column in SIMC and the corresponding locality type names.
        """
        df = self.get_registry("WMRODZ")
        self._rm = dict(zip(df["RM"].values, df["NAZWA_RM"].values))

    def get_rm(self, type_id: str | None = None, default: Any = None) -> str | None:
        """
        Get locality type (RM - Rodzaj Miejscowości) based on data from WMRODZ.

        WMRODZ is a suplementary dataset to SIMC. It contains a mapping between
        the RM column in SIMC and the corresponding locality type names.
        """
        if not self._rm:
            self.memoize_rm()
        return self._rm.get(type_id, default)

    def encode_subdivision(
        self, column: str, value: str, terc: TERC | None = None
    ) -> str | None:
        """
        Encode a subdivision code from a TERC-like registry.
        """
        encoded = None
        if terc:
            encoded = getattr(terc, column.lower(), None)
        if value:
            df = self.get_registry("TERC")
            try:
                encoded = df[df["NAZWA"] == value].iloc[0][column]
            except IndexError:
                pass
            if pd.isna(encoded):
                encoded = None
        return encoded

    def _terc_relevance_sort(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.sort_values(
            "NAZWA_DOD",
            key=lambda vector: vector.apply(self.NAZWA_DOD_RELEVANCE.get),
            ascending=False,
        )
        df = df.sort_values(
            "RODZ",
            key=lambda vector: vector.apply(self.RODZ_RELEVANCE.get),
            ascending=False,
        )
        return df

    def _filter_registry(
        self, df: pd.DataFrame, filters: dict[str, Any], check_powiat_city: bool = False
    ) -> tuple[pd.DataFrame, str | None, str | None]:
        column_stopped = None
        powiat_rights = None
        for column, value in filters.items():
            if check_powiat_city and column == "POW":
                mask = df["NAZWA_DOD"].str.contains(self.POWIAT_CITY_NAZWA_DOD)
                if mask.any():
                    powiat_rights = df[mask].iloc[0]["POW"]
                    if filters["GMI"] is None:
                        filters[column] = value = powiat_rights

            cur_results = df[
                df[column].notna() if value is None else df[column] == value
            ]

            if cur_results.empty:
                column_stopped = column
                break

            df = cur_results
        return df, column_stopped, powiat_rights

    def search_terc(self, subdivisions: Subdivisions) -> TERC:
        """
        Search for a TERC code based on given subdivisions.
        """
        result = TERC()
        df = self.get_registry("TERC")
        filters = {
            "NAZWA": subdivisions.name,
            "WOJ": self.encode_subdivision("WOJ", subdivisions.woj),
            "POW": self.encode_subdivision("POW", subdivisions.pow),
            "GMI": self.encode_subdivision("GMI", subdivisions.gmi),
        }
        check_powiat_city = filters["GMI"] in ("01", None)

        df, column_stopped, powiat_rights = self._filter_registry(
            df, filters=filters, check_powiat_city=check_powiat_city
        )

        if column_stopped not in {"NAZWA", "WOJ"}:
            df = self._terc_relevance_sort(df)
            top = df.iloc[0]
            gmi = top["GMI"]
            rodz = top["RODZ"]

            result = TERC(
                sub=subdivisions,
                woj=top["WOJ"],
                pow=top["POW"],
                gmi=gmi if not pd.isna(gmi) else None,
                rodz=rodz if not pd.isna(rodz) else None,
                powiat_rights=powiat_rights,
            )

        return result

    def search_simc(self, subdivisions: Subdivisions, terc: TERC | None = None) -> SIMC:
        """
        Search for a SIMC record based on given subdivision codes and TERC record.
        """
        result = SIMC()
        df = self.get_registry("SIMC")
        filters = {
            "NAZWA": subdivisions.name,
            "WOJ": self.encode_subdivision("WOJ", subdivisions.woj, terc=terc),
            "POW": self.encode_subdivision("POW", subdivisions.pow, terc=terc),
            "GMI": self.encode_subdivision("GMI", subdivisions.gmi, terc=terc),
        }
        df, column_stopped, _ = self._filter_registry(df, filters=filters)

        if column_stopped not in {"NAZWA", "WOJ"}:
            df = df.sort_values(
                "RM",
                key=lambda vector: vector.apply(self.WMRODZ_RELEVANCE.get),
                ascending=False,
            )

            top = df.iloc[0]
            rm = top["RM"]
            result = SIMC(
                sub=subdivisions,
                sym=top["SYM"],
                sympod=top["SYMPOD"],
                rm=rm,
                rm_nazwa=self.get_rm(rm),
            )

        return result

    def search_nts(self, subdivisions: Subdivisions, terc: TERC | None = None) -> NTS:
        """
        Search for an NTS registry entry matching given subdivisions.
        """
        result = NTS()

        df = self.get_registry("NTS")
        filters = {
            "WOJ": self.encode_subdivision("WOJ", subdivisions.woj, terc=terc),
            "POW": self.encode_subdivision("POW", subdivisions.pow, terc=terc),
            "GMI": self.encode_subdivision("GMI", subdivisions.gmi, terc=terc),
        }
        df, column_stopped, _ = self._filter_registry(df, filters=filters)

        if column_stopped != "WOJ":
            df = self._terc_relevance_sort(df)
            top = df.iloc[0]
            result = NTS(
                sub=subdivisions,
                poziom=top["POZIOM"],
                region=top["REGION"],
                woj=top["WOJ"],
                podreg=top["PODREG"],
                pow=top["POW"],
                gmi=top["GMI"],
                rodz=top["RODZ"],
                powiat_rights=terc.powiat_rights if terc else None,
            )

        return result

    def search(self, subdivisions: Subdivisions) -> TERYT:
        """Search for TERYT data from subdivisions given."""
        terc = self.search_terc(subdivisions)
        return TERYT(
            sub=subdivisions,
            terc=terc,
            simc=self.search_simc(subdivisions, terc=terc),
            nts=self.search_nts(subdivisions, terc=terc),
        )
