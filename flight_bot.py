import logging
from typing import Any, Dict, List, Optional
import requests
from config import API_DOM_URL, API_INTER_URL

logger = logging.getLogger(__name__)
class FlightScheduleBot:
    def __init__(self) -> None:
        pass

    def _fetch_api(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return response.json()
            logger.warning(f"API returned non-200 status {response.status_code} for {url}")
            return None
        except requests.RequestException as exc:
            logger.error(f"API request failed for {url}: {exc}")
            return None

    def _normalize_flights(self, data: Optional[Dict[str, Any]], departure: str) -> List[Dict[str, Any]]:
        if not data:
            return []
        flights = data.get("data", [])
        normalized: List[Dict[str, Any]] = []
        for raw in flights:
            if not isinstance(raw, dict):
                continue
            item = {
                "id": raw.get("id"),
                "operator": raw.get("operator"),
                "schedule": raw.get("schedule"),
                "estimate": raw.get("estimate"),
                "flightno": raw.get("flightno"),
                "gatenumber": raw.get("gatenumber"),
                "flightstat": raw.get("flightstat"),
                "fromtolocation": raw.get("fromtolocation"),
                "departure": departure,
            }
            normalized.append(item)
        return normalized

    def _get_all_flights_for_date(self, date: str) -> List[Dict[str, Any]]:
        dom = self._fetch_api(API_DOM_URL)
        inter = self._fetch_api(API_INTER_URL)
        dom_list = self._normalize_flights(dom, "D")
        inter_list = self._normalize_flights(inter, "I")
        all_flights = dom_list + inter_list
        # Filter by date if schedule contains date string
        filtered = [f for f in all_flights if f.get("schedule") and str(date) in str(f.get("schedule"))]
        # Sort by schedule text when possible
        try:
            filtered.sort(key=lambda x: str(x.get("schedule")))
        except Exception:
            pass
        return filtered

    def get_flights_by_date(self, date: str) -> List[Dict[str, Any]]:
        return self._get_all_flights_for_date(date)

    def get_flight_info(self, flight_code: str, date: str) -> Optional[Dict[str, Any]]:
        flights = self._get_all_flights_for_date(date)
        for f in flights:
            if str(f.get("flightno", "")).upper() == flight_code.upper():
                return f
        return None

    def get_flight_info_by_id(self, flight_id: str) -> Optional[Dict[str, Any]]:
        dom = self._normalize_flights(self._fetch_api(API_DOM_URL), "D")
        inter = self._normalize_flights(self._fetch_api(API_INTER_URL), "I")
        for f in dom + inter:
            if str(f.get("id")) == str(flight_id):
                return f
        return None