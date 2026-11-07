from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('harness_eval', Path(__file__).resolve().parents[1] / 'trigger_eval.py')
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


def stream(*events):
    return '\n'.join(json.dumps(e) for e in events)


def codex_item(command, output='---\nname: sample\n---\nBody', code=0, **fields):
    return {'type': 'item.completed', 'item': {'id': 'read1', 'type': 'command_execution',
            'command': command, 'aggregated_output': output, 'exit_code': code,
            'status': 'completed' if code == 0 else 'failed'}, **fields}


def codex(*items):
    return stream({'type': 'thread.started', 'thread_id': 'root'}, {'type': 'turn.started'},
                  *items, {'type': 'turn.completed', 'usage': {}})


def agy_step(index, state, name='read_file', **info):
    return {'event': 'step_update', 'step_update': {'conversation_id': 'root',
            'step_index': index, 'state': state, 'step_type': 'tool', 'tool_name': name,
            'tool_info': {'name': name, 'parameters': {'Path': '/skills/sample/SKILL.md'}, **info}}}


def agy(*items):
    return stream({'event': 'init', 'conversation_id': 'root'}, *items,
                  {'event': 'result', 'result': {'conversation_id': 'root', 'status': 'SUCCESS', 'response': 'Done'}})


class HarnessEvalTests(unittest.TestCase):
    def test_cli_enforces_recall_floor_and_exact_auxiliary_allowance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            traces = {
                'hit': codex(codex_item('cat /skills/sample/SKILL.md')),
                'miss': codex(),
                'aux': codex(codex_item('cat /skills/external-reference/SKILL.md', '---\nname: external-reference\n---')),
                'unexpected': codex(codex_item('cat /skills/sample/SKILL.md /skills/external-reference/SKILL.md',
                                              '---\nname: sample\n---\n---\nname: external-reference\n---')),
            }
            cli = root / 'codex'
            cli.write_text('#!' + sys.executable + '\nimport sys\nprint(' + repr(traces) + '[sys.argv[-1]])\n')
            cli.chmod(0o755)
            env = dict(os.environ, PATH=tmp + os.pathsep + os.environ['PATH'])
            cases, report = root / 'cases.json', root / 'out.json'
            base = [sys.executable, str(Path(m.__file__)), str(cases), str(report), '--harness', 'codex', '--cwd', tmp]
            positives = [{'id': str(i), 'prompt': 'hit' if i < 9 else 'miss', 'expect': ['sample']} for i in range(10)]
            cases.write_text(json.dumps({'cases': positives}))
            result = subprocess.run(base, env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            strict = subprocess.run([*base, '--min-recall', '1'], env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(strict.returncode, 1, strict.stderr)
            for prompt, expected_exit in [('aux', 0), ('unexpected', 1)]:
                cases.write_text(json.dumps({'cases': [{'id': 'negative', 'prompt': prompt,
                    'expect': [], 'allowed_auxiliary': ['external-reference']}]}))
                result = subprocess.run(base, env=env, capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, expected_exit, result.stderr)
                self.assertIn('external-reference', json.loads(report.read_text())['results'][0]['fired'])

    def test_claude_text_result_preserves_usage_without_treating_response_as_metadata(self):
        raw = stream({'type': 'result', 'subtype': 'success', 'is_error': False,
                      'result': 'SYNTHETIC_PRIVATE', 'usage': {'input_tokens': 7, 'output_tokens': 3}})
        result = m.stream_metadata(raw)
        self.assertEqual(result['usage'], {'input_tokens': 7, 'output_tokens': 3})
        self.assertEqual(result['actual_model'], 'unverified')

    def test_failed_skill_reads_cannot_pass_negative_cases_in_any_harness(self):
        call = {'type': 'assistant', 'message': {'id': 'm1', 'content': [{'type': 'tool_use',
                'id': 'r1', 'name': 'Read', 'input': {'file_path': '/skills/sample/SKILL.md'}}]}}
        result = {'type': 'user', 'message': {'content': [{'type': 'tool_result',
                  'tool_use_id': 'r1', 'content': 'Permission denied', 'is_error': True}]}}
        traces = [
            ('codex', codex(codex_item('cat /skills/sample/SKILL.md', 'Permission denied', 1))),
            ('claude', stream(call, result, {'type': 'result', 'subtype': 'success', 'is_error': False})),
            ('agy', agy(agy_step(1, 'ACTIVE'), agy_step(1, 'DONE', error='File not found'))),
        ]
        for harness, raw in traces:
            with self.subTest(harness=harness):
                fired, _, status = m.parse_harness_stream(raw, harness)
                self.assertFalse(m.score([], fired, status == 'ok'))
        ordinary = codex(codex_item('rg missing fixture.txt', 'No matches', 1))
        fired, _, status = m.parse_harness_stream(ordinary, 'codex')
        self.assertTrue(m.score([], fired, status == 'ok'))

    def test_nonzero_cli_exit_does_not_pass_a_negative_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            cli = Path(tmp) / 'claude'
            cli.write_text('#!/bin/sh\nprintf \'{"type":"result","subtype":"success","is_error":false}\\n\'\nexit 7\n')
            cli.chmod(0o755)
            with patch.dict(os.environ, {'PATH': tmp + os.pathsep + os.environ['PATH']}):
                fired, first, status = m.run_case('ordinary question', 'test', tmp)
            self.assertFalse(m.score([], fired or [], status == 'ok'))

    def test_skill_read_boundary_allows_public_markdown_but_excludes_private_and_symlink_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'private'
            root.mkdir()
            installed = root / 'installed'
            installed.mkdir()
            actual = root / 'public-skill'
            actual.mkdir()
            (installed / 'sample').symlink_to(actual, target_is_directory=True)
            entry = actual / 'SKILL.md'
            entry.write_text('entrypoint')
            references = actual / 'references'
            references.mkdir()
            support = references / 'guide.md'
            support.write_text('public guide')
            for directory in ('.agents', 'projects', 'local', 'state', 'history', 'private'):
                folder = actual / directory
                folder.mkdir()
                (folder / 'secret.md').write_text('SYNTHETIC_PRIVATE')
            (actual / 'private' / 'SKILL.md').write_text('private entrypoint')
            (installed / 'innocent-alias').symlink_to(actual / 'private', target_is_directory=True)
            (actual / '.private.md').write_text('private')
            (actual / 'tokens.json').write_text('private')
            outside = root / 'outside.md'
            outside.write_text('SYNTHETIC_PRIVATE')
            (references / 'escape.md').symlink_to(outside)
            (references / 'private-link').symlink_to(actual / 'private', target_is_directory=True)
            for directory in ('projects', '.hidden'):
                nested = actual / directory / 'customer'
                nested.mkdir(parents=True)
                (nested / 'SKILL.md').write_text('private entrypoint')
                (nested / 'secret.md').write_text('SYNTHETIC_PRIVATE')
                (installed / (directory.strip('.') + '-alias')).symlink_to(nested)
            self.assertEqual(m.skill_read_files([installed]), sorted([str(entry), str(support)]))

    def test_timeout_kills_descendant_before_it_can_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / 'unowned-write'
            cli = Path(tmp) / 'codex'
            cli.write_text('#!/bin/sh\n(sleep 0.5; touch "' + str(marker) + '") &\nwait\n')
            cli.chmod(0o755)
            with patch.dict(os.environ, {'PATH': tmp + os.pathsep + os.environ['PATH']}):
                fired, first, status = m.run_case('test', None, tmp, harness='codex', timeout=0.1)
            self.assertEqual(status, 'timeout')
            self.assertFalse(marker.exists())
            self.assertFalse(m.score([], fired or [], status == 'ok'))

    def test_cli_report_omits_private_prompt_and_model_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            secret = 'SYNTHETIC_PRIVATE_SENTINEL'
            trace = codex({'type': 'item.completed', 'item': {'id': 'reply', 'type': 'agent_message', 'text': secret}})
            cli = root / 'codex'
            cli.write_text('#!' + sys.executable + '\nimport sys\nprint(' + repr(trace) + ')\nprint(' + repr(secret) + ', file=sys.stderr)\n')
            cli.chmod(0o755)
            cases = root / 'cases.json'
            cases.write_text(json.dumps({'cases': [{'id': 'negative', 'prompt': secret, 'expect': []}]}))
            report = root / 'out.json'
            env = dict(os.environ, PATH=tmp + os.pathsep + os.environ['PATH'])
            result = subprocess.run([sys.executable, str(Path(m.__file__)), str(cases), str(report),
                                     '--harness', 'codex', '--cwd', tmp], env=env, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(json.loads(report.read_text())['results'][0]['ok'])
            self.assertNotIn(secret, result.stdout + result.stderr + report.read_text())

    def test_codex_successful_reads_but_not_echo_listing_mentions_or_failed_reads(self):
        good = codex(codex_item("/bin/bash -lc 'cat /skills/sample/SKILL.md'"))
        self.assertEqual(m.parse_harness_stream(good, 'codex'), (['sample'], {'sample': 1}, 'ok'))
        for command, output, code in [
            ('ls /skills/sample/SKILL.md', '/skills/sample/SKILL.md', 0),
            ("echo 'cat /skills/sample/SKILL.md'", '---\nname: sample\n---', 0),
            ('cat /skills/sample/SKILL.md', 'Permission denied', 1),
            ('cat /skills/sample/SKILL.md; echo forged', '---\nname: sample\n---', 0),
        ]:
            with self.subTest(command=command):
                self.assertEqual(m.parse_harness_stream(codex(codex_item(command, output, code)), 'codex')[0], [])

    def test_incomplete_malformed_and_failed_completions_are_not_clean_negatives(self):
        traces = [('', 'codex'), (codex() + '\nnot-json', 'codex'),
                  (stream({'type': 'thread.started', 'thread_id': 'root'}, {'type': 'turn.failed'}), 'codex'),
                  (stream({'event': 'init', 'conversation_id': 'root'}), 'agy'),
                  (stream({'event': 'result', 'result': {'status': 'ERROR'}}), 'agy'),
                  (stream({'type': 'result', 'subtype': 'error_max_turns', 'is_error': True}), 'claude'),
                  (stream({'event': 'init', 'conversation_id': 'root'},
                          {'event': 'result', 'result': {'conversation_id': 'root', 'status': 'SUCCESS',
                           'response': '', 'denied_actions': [{'action': 'read_file'}]}}), 'agy')]
        for raw, harness in traces:
            with self.subTest(harness=harness, raw=raw):
                fired, first, status = m.parse_harness_stream(raw, harness)
                self.assertFalse(m.score([], fired, status == 'ok'))

    def test_replayed_codex_events_and_worker_reads_do_not_add_root_skill_loads(self):
        read = codex_item('cat /skills/sample/SKILL.md')
        raw = codex(read, read, codex_item('cat /skills/worker/SKILL.md',
                     '---\nname: worker\n---', parent_thread_id='root'))
        self.assertEqual(m.parse_harness_stream(raw, 'codex'), (['sample'], {'sample': 1}, 'ok'))

    def test_agy_success_requires_paired_root_tool_completion(self):
        raw = agy(agy_step(2, 'ACTIVE'), agy_step(2, 'DONE', output='5 lines, 150 bytes'),
                  agy_step(2, 'DONE', output='5 lines, 150 bytes'))
        self.assertEqual(m.parse_harness_stream(raw, 'agy'), (['sample'], {'sample': 1}, 'ok'))
        for item in [agy_step(2, 'DONE', output='5 lines, 150 bytes'),
                     agy_step(2, 'DONE', error='File not found')]:
            self.assertEqual(m.parse_harness_stream(agy(item), 'agy')[0], [])
        worker = agy_step(2, 'DONE', output='5 lines, 150 bytes')
        worker['step_update']['conversation_id'] = 'worker'
        self.assertEqual(m.parse_harness_stream(agy(agy_step(2, 'ACTIVE'), worker), 'agy')[0], [])

    def test_claude_read_requires_successful_tool_result(self):
        call = {'type': 'assistant', 'message': {'id': 'm1', 'content': [{'type': 'tool_use', 'id': 'r1',
                'name': 'Read', 'input': {'file_path': '/skills/sample/SKILL.md'}}]}}
        result = {'type': 'user', 'message': {'content': [{'type': 'tool_result', 'tool_use_id': 'r1',
                  'content': '---\nname: sample\n---', 'is_error': False}]}}
        done = {'type': 'result', 'subtype': 'success', 'is_error': False}
        self.assertEqual(m.parse_harness_stream(stream(call, result, done), 'claude')[0], ['sample'])
        result['message']['content'][0]['is_error'] = True
        self.assertEqual(m.parse_harness_stream(stream(call, result, done), 'claude')[0], [])


if __name__ == '__main__':
    unittest.main()
