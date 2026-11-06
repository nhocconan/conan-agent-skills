from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "trigger_eval.py"
SPEC = importlib.util.spec_from_file_location("trigger_eval", MODULE_PATH)
assert SPEC and SPEC.loader
trigger_eval = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(trigger_eval)

SET_PATH = Path(__file__).resolve().parents[1] / "trigger-set.synthetic.json"


def assistant(mid, *blocks):
    return json.dumps({"type": "assistant", "message": {"id": mid, "content": list(blocks)}})


def tool(name, **inp):
    return {"type": "tool_use", "name": name, "input": inp}


class ParseStreamTests(unittest.TestCase):
    def test_skill_tool_use_and_read_of_skill_md_with_turns(self):
        stream = "\n".join([
            json.dumps({"type": "system"}),
            assistant("m1", {"type": "text", "text": "thinking"}),
            assistant("m2", tool("Skill", skill="plugin:web-qa")),
            assistant("m3", tool("Read", file_path="/home/x/.claude/skills/design-qa/SKILL.md"),
                      tool("Read", file_path="/repo/README.md")),
        ])
        fired, first = trigger_eval.parse_stream(stream)
        self.assertEqual(fired, ["design-qa", "web-qa"])
        self.assertEqual(first, {"web-qa": 2, "design-qa": 3})

    def test_malformed_and_non_assistant_lines_are_skipped(self):
        stream = "\n".join(["not json", "[1,2]", '{"type":"assistant","message":"x"}',
                            assistant("m1", tool("Skill", skill="a"))])
        self.assertEqual(trigger_eval.parse_stream(stream), (["a"], {"a": 1}))

    def test_events_sharing_a_message_id_are_one_turn_and_first_fire_wins(self):
        stream = "\n".join([assistant("m1", tool("Skill", skill="a")),
                            assistant("m1", tool("Skill", skill="b")),
                            assistant("m2", tool("Skill", skill="a"))])
        self.assertEqual(trigger_eval.parse_stream(stream)[1], {"a": 1, "b": 1})

    def test_empty_stream(self):
        self.assertEqual(trigger_eval.parse_stream(""), ([], {}))


class ScoreTests(unittest.TestCase):
    def test_score_positive_negative_and_failed_run(self):
        self.assertTrue(trigger_eval.score(["a", "b"], ["b", "c"]))
        self.assertFalse(trigger_eval.score(["a"], ["c"]))
        self.assertTrue(trigger_eval.score([], []))
        self.assertFalse(trigger_eval.score([], ["c"]))
        self.assertFalse(trigger_eval.score(["a"], ["a"], ok_status=False))

    def test_recall_at_uses_first_turn_of_expected_skill_only(self):
        rows = [
            {"expect": ["a"], "first_turns": {"a": 2}},
            {"expect": ["a"], "first_turns": {"a": 5, "z": 1}},
            {"expect": ["a"], "first_turns": {}},
            {"expect": [], "first_turns": {"z": 1}},
        ]
        self.assertEqual(trigger_eval.recall_at(rows, 3), "1/3")
        self.assertEqual(trigger_eval.recall_at(rows, 6), "2/3")


class TriggerSetTests(unittest.TestCase):
    def test_synthetic_set_has_no_real_cases_and_near_miss_negatives(self):
        cases = json.loads(SET_PATH.read_text(encoding="utf-8"))["cases"]
        self.assertEqual({c["src"] for c in cases}, {"synthetic", "negative"})
        self.assertEqual(len({c["id"] for c in cases}), len(cases))
        self.assertEqual(sum(1 for c in cases if c.get("near_miss")), 4)
        self.assertTrue(all(c["expect"] == [] for c in cases if c["src"] == "negative"))


if __name__ == "__main__":
    unittest.main()
