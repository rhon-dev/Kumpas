# Replay test invocation fix

Scope: final quality advisory Q1 only. Runner work remains deferred.

RED: package-qualified `unittest benchmarking.test_host_producer_replay.PreflightNegatives.test_wrong_run -v` returned exit 1 with ModuleNotFoundError for host_fixture_replay in test setup. This is test harness import-path behavior, not a production replay defect.

The existing discovery invocation places benchmarking on sys.path; the package-qualified invocation did not. Preserve the before snapshot and align test setup with the supported sibling-import layout. No production, model, participant store or historical fixture edits.
