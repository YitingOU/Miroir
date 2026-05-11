from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


class OpenClawWorkspaceContractTest(unittest.TestCase):
    def test_skill_defaults_to_live_openclaw_workspace(self) -> None:
        skill = read("SKILL.md")

        self.assertRegex(skill, r"FINAL_ROOT=.*~/openclaw-workspace/\[agent-name\]")
        self.assertRegex(skill, r"BUILD_ROOT=.*~/openclaw-workspace/\.staging/\[agent-name\]-\[run-id\]")
        self.assertIn("Do not stop at a project-local export", skill)
        self.assertRegex(skill, r"[Cc]reate a new unique final agent directory")
        self.assertNotIn("No installation into a live OpenClaw workspace unless explicitly requested", skill)
        self.assertNotIn("Only install into a live OpenClaw workspace when the user explicitly asks", skill)

    def test_skill_stages_before_touching_live_workspace(self) -> None:
        skill = read("SKILL.md")

        self.assertIn("Create a staging build root before research starts", skill)
        self.assertIn("Do not create or modify the final live agent directory until the staging build passes validation", skill)
        self.assertIn('python3 scripts/quality_check.py "$BUILD_ROOT"', skill)
        self.assertIn('python3 scripts/quality_check.py "$FINAL_ROOT"', skill)
        self.assertIn("Install a new agent with an atomic same-filesystem rename", skill)
        self.assertNotIn("Create the target agent directory before research starts. The default target is the live", skill)

    def test_staging_is_unique_and_same_filesystem_as_final(self) -> None:
        skill = read("SKILL.md")

        self.assertIn("BUILD_ROOT=~/openclaw-workspace/.staging/[agent-name]-[run-id]", skill)
        self.assertIn("RUN_ID", skill)
        self.assertIn("same filesystem", skill)
        self.assertIn("Do not reuse a staging directory", skill)
        self.assertNotIn("BUILD_ROOT=./openclaw-workspace/.staging/[agent-name]", skill)

    def test_staging_visibility_contract_is_explicit(self) -> None:
        skill = read("SKILL.md")

        self.assertIn("OpenClaw runtime must ignore `~/openclaw-workspace/.staging/`", skill)
        self.assertRegex(skill, r"If that ignore behavior is not\s+guaranteed")
        self.assertIn("use another non-scanned staging directory on the same filesystem", skill)
        self.assertRegex(skill, r"stop and ask\s+before writing a live staging directory")

    def test_staging_cleanup_policy_is_explicit(self) -> None:
        skill = read("SKILL.md")

        self.assertIn("Staging Cleanup", skill)
        self.assertIn("After a successful new-agent rename", skill)
        self.assertIn("remove the empty `.staging` parent only if it is empty", skill)
        self.assertIn("If validation or install fails, keep BUILD_ROOT for inspection and report its path", skill)
        self.assertIn("Never retry into the same BUILD_ROOT", skill)

    def test_new_install_and_existing_update_are_separate_flows(self) -> None:
        skill = read("SKILL.md")

        self.assertIn("New Agent Install", skill)
        self.assertIn("Existing Agent Update", skill)
        self.assertIn("Do not move or copy the whole staging directory over an existing agent", skill)
        self.assertRegex(skill, r"[Pp]atch only the selected files in FINAL_ROOT")
        self.assertIn("atomic same-filesystem rename", skill)

    def test_default_bullets_are_consistently_capitalized(self) -> None:
        skill = read("SKILL.md")

        self.assertIn("- Create a new unique final agent directory", skill)
        self.assertNotIn("- create a new unique final agent directory", skill)

    def test_readme_documents_direct_agent_workspace_output(self) -> None:
        readme = read("README.md")

        self.assertIn("writes it directly to `~/openclaw-workspace/[agent-name]/`", readme)
        self.assertIn("stages the build before installing it", readme)
        self.assertIn("Validate the final agent workspace", readme)
        self.assertNotIn("install into a live OpenClaw workspace only when explicitly asked", readme)

    def test_persona_research_writes_to_build_root(self) -> None:
        pipeline = read("references/persona-research-pipeline.md")

        self.assertIn("$BUILD_ROOT/references/research/", pipeline)
        self.assertIn('bash scripts/download_subtitles.sh <YouTube_URL> "$BUILD_ROOT/references/sources/transcripts"', pipeline)
        self.assertIn('python3 scripts/srt_to_transcript.py "$subtitle_file" "$transcript_file"', pipeline)
        self.assertIn('transcript_file="$BUILD_ROOT/references/sources/transcripts/', pipeline)
        self.assertNotIn("Write to openclaw-workspace/[agent-name]/references/research", pipeline)

    def test_contract_paths_are_not_only_phrase_checks(self) -> None:
        skill = read("SKILL.md")
        final_mentions = re.findall(r"~/openclaw-workspace/\[agent-name\]", skill)
        build_mentions = re.findall(r"~/openclaw-workspace/\.staging/\[agent-name\]-\[run-id\]", skill)

        self.assertGreaterEqual(len(final_mentions), 2)
        self.assertGreaterEqual(len(build_mentions), 2)


if __name__ == "__main__":
    unittest.main()
