import unittest

from analytics.dashboard_ecosystem_context import project_ecosystem_context


class DashboardEcosystemContextTests(unittest.TestCase):
    def test_projects_stock_and_aligned_activity_without_identity_overreach(self) -> None:
        dashboard = {
            "schema_version": 1,
            "comparison": {
                "window_start": "2026-09-03",
                "window_end": "2026-09-04",
                "window_days": 2,
                "repositories": [
                    {
                        "repository_id": "core",
                        "repository": "FAROTECH/orbitfabric",
                        "category": "core",
                    },
                    {
                        "repository_id": "studio",
                        "repository": "FAROTECH/orbitfabric-studio",
                        "category": "product",
                    },
                ],
            },
        }

        community = [
            {
                "repository_id": "core",
                "repository": "FAROTECH/orbitfabric",
                "category": "core",
                "current_date": "2026-09-06",
                "previous_date": "2026-09-05",
                "snapshot_gap_days": "1",
                "comparable": "true",
                "stars_total": "6",
                "stars_total_delta": "1",
                "forks_total": "1",
                "forks_total_delta": "0",
                "open_issues_total": "3",
                "open_issues_total_delta": "-1",
                "open_pull_requests_total": "0",
                "open_pull_requests_total_delta": "0",
                "contributors_repo_count": "1",
                "contributors_repo_count_delta": "0",
            },
            {
                "repository_id": "studio",
                "repository": "FAROTECH/orbitfabric-studio",
                "category": "product",
                "current_date": "2026-09-06",
                "previous_date": "2026-09-05",
                "snapshot_gap_days": "1",
                "comparable": "true",
                "stars_total": "0",
                "stars_total_delta": "0",
                "forks_total": "0",
                "forks_total_delta": "0",
                "open_issues_total": "2",
                "open_issues_total_delta": "0",
                "open_pull_requests_total": "0",
                "open_pull_requests_total_delta": "0",
                "contributors_repo_count": "2",
                "contributors_repo_count_delta": "0",
            },
        ]

        development = []
        lifecycle = []
        participation = []
        for day in ("2026-09-03", "2026-09-04"):
            for repository_id in ("core", "studio"):
                development.append(
                    {
                        "date": day,
                        "repository_id": repository_id,
                        "commits_total": "2",
                        "first_party_commits": "2",
                        "automation_commits": "0",
                        "other_commits": "0",
                        "workflow_runs_total": "3",
                        "workflow_runs_success": "3",
                        "workflow_runs_failure": "0",
                        "workflow_runs_other": "0",
                    }
                )
                lifecycle.append(
                    {
                        "date": day,
                        "repository_id": repository_id,
                        "issues_opened": "1",
                        "issues_closed": "0",
                        "prs_opened": "2",
                        "prs_merged": "1",
                        "prs_closed_unmerged": "1",
                    }
                )
                participation.append(
                    {
                        "date": day,
                        "repository_id": repository_id,
                        "issue_author_events": "1",
                        "pr_author_events": "2",
                        "comment_events": "4",
                        "participants_repo_count": "1",
                        "first_party_participants_repo_count": "1",
                        "automation_participants_repo_count": "0",
                        "other_participants_repo_count": "0",
                        "participants_first_seen_repo_count": "0",
                        "other_participants_first_seen_repo_count": "0",
                    }
                )

        payload = project_ecosystem_context(
            dashboard,
            community,
            development,
            lifecycle,
            participation,
        )
        context = payload["ecosystem_context"]

        self.assertEqual(context["stock"]["current_date"], "2026-09-06")
        self.assertEqual(context["stock"]["totals"]["stars_total"], 6)
        self.assertEqual(context["stock"]["totals"]["stars_total_delta"], 1)
        self.assertEqual(context["stock"]["totals"]["open_issues_total"], 5)

        aligned = context["aligned_window"]
        self.assertEqual(aligned["development"]["first_party_commits"], 8)
        self.assertEqual(aligned["development"]["workflow_runs_total"], 12)
        self.assertEqual(aligned["lifecycle"]["prs_merged"], 4)
        self.assertEqual(aligned["participation"]["participants_repo_count"], 4)
        self.assertEqual(aligned["participation"]["other_participants_repo_count"], 0)
        self.assertTrue(aligned["participation"]["coverage_complete"])
        self.assertTrue(context["semantics"]["participant_totals_are_repo_day_sums"])
        self.assertTrue(
            context["semantics"]["other_participant_does_not_mean_external_user"]
        )

    def test_rejects_misaligned_stock_snapshot_boundaries(self) -> None:
        dashboard = {
            "schema_version": 1,
            "comparison": {
                "window_start": "2026-09-04",
                "window_end": "2026-09-04",
                "window_days": 1,
                "repositories": [
                    {
                        "repository_id": "core",
                        "repository": "FAROTECH/orbitfabric",
                        "category": "core",
                    },
                    {
                        "repository_id": "studio",
                        "repository": "FAROTECH/orbitfabric-studio",
                        "category": "product",
                    },
                ],
            },
        }
        community = []
        for repository_id, current_date in (("core", "2026-09-06"), ("studio", "2026-09-05")):
            row = {
                "repository_id": repository_id,
                "repository": repository_id,
                "category": "core",
                "current_date": current_date,
                "previous_date": "2026-09-04",
                "snapshot_gap_days": "1",
                "comparable": "true",
            }
            for field in (
                "stars_total",
                "forks_total",
                "open_issues_total",
                "open_pull_requests_total",
                "contributors_repo_count",
            ):
                row[field] = "0"
                row[f"{field}_delta"] = "0"
            community.append(row)

        zero_development = [
            {
                "date": "2026-09-04",
                "repository_id": repository_id,
                "commits_total": "0",
                "first_party_commits": "0",
                "automation_commits": "0",
                "other_commits": "0",
                "workflow_runs_total": "0",
                "workflow_runs_success": "0",
                "workflow_runs_failure": "0",
                "workflow_runs_other": "0",
            }
            for repository_id in ("core", "studio")
        ]
        zero_lifecycle = [
            {
                "date": "2026-09-04",
                "repository_id": repository_id,
                "issues_opened": "0",
                "issues_closed": "0",
                "prs_opened": "0",
                "prs_merged": "0",
                "prs_closed_unmerged": "0",
            }
            for repository_id in ("core", "studio")
        ]
        zero_participation = [
            {
                "date": "2026-09-04",
                "repository_id": repository_id,
                "issue_author_events": "0",
                "pr_author_events": "0",
                "comment_events": "0",
                "participants_repo_count": "0",
                "first_party_participants_repo_count": "0",
                "automation_participants_repo_count": "0",
                "other_participants_repo_count": "0",
                "participants_first_seen_repo_count": "0",
                "other_participants_first_seen_repo_count": "0",
            }
            for repository_id in ("core", "studio")
        ]

        with self.assertRaises(ValueError):
            project_ecosystem_context(
                dashboard,
                community,
                zero_development,
                zero_lifecycle,
                zero_participation,
            )


if __name__ == "__main__":
    unittest.main()
