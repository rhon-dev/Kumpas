import 'dart:convert';
import 'dart:io';

/// Trusted local test bridge. Python validates the pinned manifest, 42 sources,
/// producer suite/ledger and all artifact digests on EVERY load. It transfers
/// those same in-memory bytes as base64, not a stale preflight boolean. Dart
/// never rereads fixture paths after verification; no crypto dependency added.
/// Trusts local interpreter/code/pipe, not a hostile concurrent filesystem.
class HostFixture {
  HostFixture._(this.receipt, this._bytes);
  final Map<String, dynamic> receipt;
  final Map<String, List<int>> _bytes;
  static const runId = '323291af-c067-46dc-bae1-067d62fab10b';
  static const digest =
      '3279cb7d01075a9192f2566ae5573dd6137a23c6710ef1d0a590b78564fe0fed';

  static HostFixture load() {
    final repo = Directory.current.path.endsWith('/app')
        ? Directory.current.parent
        : Directory.current;
    final result = Process.runSync('/opt/homebrew/bin/python3.11', [
      '-E',
      '${repo.path}/benchmarking/host_fixture_replay.py',
      'bundle',
    ], workingDirectory: repo.path);
    if (result.exitCode != 0) {
      throw StateError('native_fixture_preflight_failed');
    }
    final bundle = jsonDecode(result.stdout as String) as Map<String, dynamic>;
    final receipt = bundle['receipt'] as Map<String, dynamic>;
    if (receipt['run_id'] != runId ||
        receipt['manifest_sha256'] != digest ||
        receipt['source_count'] != 42 ||
        receipt['producer_tests'] != 5 ||
        receipt['synthetic_origin'] != true) {
      throw StateError('native_fixture_binding_mismatch');
    }
    final encoded = bundle['payload_base64'] as Map<String, dynamic>;
    if (encoded.length != 11) {
      throw StateError('native_fixture_payload_missing');
    }
    final bytes = encoded.map(
      (key, value) => MapEntry(key, base64Decode(value as String)),
    );
    return HostFixture._(receipt, bytes);
  }

  String text(String name) => utf8.decode(_bytes[name]!);
  dynamic json(String name) => jsonDecode(text(name));
  Map<String, dynamic> get study => json('study.json') as Map<String, dynamic>;
  Map<String, dynamic> get event =>
      json('attempt-event.json') as Map<String, dynamic>;
  List<Map<String, dynamic>> get calls =>
      (study['control_calls'] as List).cast<Map<String, dynamic>>();
  Map<String, dynamic> control(String stage, String method, {int index = 0}) =>
      calls
          .where((r) => r['stage'] == stage && r['method'] == method)
          .elementAt(index);
}
