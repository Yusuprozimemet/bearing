"""The lines each area gained and lost, week by week, from the files each commit changed."""

from datetime import UTC, datetime

from bearing.direction.config import area_of


def churn(commits, areas):
    totals = {}
    for committed_at, files in commits:
        # Weeks are ISO weeks of the UTC date, so a commit near midnight lands where the other clocks put it.
        day = datetime.fromisoformat(committed_at).astimezone(UTC).date()
        year, week, _ = day.isocalendar()
        iso_week = f"{year}-W{week:02d}"
        for path, added, deleted in files:
            key = (iso_week, area_of(path, areas))
            gained, lost = totals.get(key, (0, 0))
            totals[key] = (gained + added, lost + deleted)
    return sorted(
        (week, area, added, deleted)
        for (week, area), (added, deleted) in totals.items()
    )
