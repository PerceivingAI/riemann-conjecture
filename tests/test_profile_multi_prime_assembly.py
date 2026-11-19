from scripts import profile_multi_prime_assembly as profiler


def test_profile_frames_preserve_ranking_and_statistics_across_layouts(tmp_path):
    def export(layout):
        script = layout / 'repo' / 'scripts'
        dependency = layout / 'lib' / 'site-packages'
        second_dependency = layout / 'user-lib'
        roots = (('dependency', dependency), ('dependency', second_dependency),
                 ('stdlib', layout / 'lib'), ('repo:scripts', script))
        filenames = [script / 'first' / 'shared.py', script / 'second' / 'shared.py',
                     dependency / 'pkg' / 'shared.py', second_dependency / 'pkg' / 'shared.py',
                     layout / 'temp' / 'first' / 'private.py', layout / 'temp' / 'second' / 'private.py',
                     layout / 'lib' / 'contextlib.py', '~', '<frozen abc>']
        keys = [(str(filename), 19, 'run') for filename in filenames]
        stats = {key: (i + 1, i + 2, i / 10, float(i), {}) for i, key in enumerate(keys)}
        rows = profiler._profile_rows(stats, roots)
        assert [(row['primitive_calls'], row['calls'], row['exclusive_seconds'], row['cumulative_seconds'])
                for row in rows] == [stats[key][:4] for key in reversed(keys)]
        assert all((row['line'], row['function']) == (19, 'run') for row in rows)
        return rows

    rows = export(tmp_path / 'private-layout-one')
    assert rows == export(tmp_path / 'private-layout-two')
    assert [(row['source'], row['source_instance']) for row in rows] == [
        ('frozen:abc', 1), ('builtin', 1), ('stdlib:contextlib.py', 1),
        ('unclassified', 1), ('unclassified', 2),
        ('dependency:pkg/shared.py', 1), ('dependency:pkg/shared.py', 2),
        ('repo:scripts/second/shared.py', 1), ('repo:scripts/first/shared.py', 1),
    ]


def test_provenance_does_not_persist_arbitrary_thread_environment(monkeypatch):
    monkeypatch.setenv('OMP_NUM_THREADS', '2, 1')
    monkeypatch.setenv('OPENBLAS_NUM_THREADS', '/private-layout/identity')
    monkeypatch.delenv('MKL_NUM_THREADS', raising=False)
    provenance = profiler._provenance()
    assert provenance['thread_environment']['OMP_NUM_THREADS'] == '2, 1'
    assert provenance['thread_environment']['OPENBLAS_NUM_THREADS'] == 'unrecognized'
    assert provenance['thread_environment']['MKL_NUM_THREADS'] is None
