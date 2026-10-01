"""Run on macOS/Linux/WSL: python3 tests/test_bash.py.

Tests use a real pseudo-terminal and an isolated home/repo; no personal files
are changed. Only Python's standard library is required.
"""
import fcntl
import os
from pathlib import Path
import pty
import select
import shutil
import struct
import subprocess
import tempfile
import termios
import time
import unittest


class BashScriptsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agent-scripts-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "repo with spaces"
        self.home = self.root / "home with spaces"
        self.home.mkdir()
        shutil.copytree(Path(__file__).resolve().parents[1] / "scripts", self.repo / "scripts")
        self.write(self.repo / "AGENTS.md", "repo instructions\n")
        self.payload = self.root / "remote AGENTS.md"
        self.write(self.payload, "remote instructions\n")
        self.bin = self.root / "bin"
        self.write(self.bin / "curl", '''#!/usr/bin/env bash
set -e
while (($#)); do
    case "$1" in
        -o) destination=$2; shift 2;;
        https://*) printf '%s\\n' "$1" > "$FAKE_CURL_LOG"; shift;;
        *) shift;;
    esac
done
[[ ${FAKE_CURL_EXIT:-0} == 0 ]] || exit "$FAKE_CURL_EXIT"
if [[ ${FAKE_CURL_EMPTY:-0} == 1 ]]; then
    : > "$destination"
else
    cp "$FAKE_CURL_CONTENT" "$destination"
fi
printf '%s\\n' "$destination" >> "$FAKE_CURL_LOG"
''')
        (self.bin / "curl").chmod(0o755)
        self.env = dict(
            os.environ, HOME=str(self.home), TERM="xterm", COLUMNS="100",
            PATH=str(self.bin) + os.pathsep + os.environ["PATH"],
            FAKE_CURL_CONTENT=str(self.payload), FAKE_CURL_LOG=str(self.root / "curl.log"),
            AGENTS_REF="test-ref",
        )

    @staticmethod
    def write(path, content):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def run_script(self, name, keys, command=None, expected_exit=0):
        master, slave = pty.openpty()
        fcntl.ioctl(slave, termios.TIOCSWINSZ, struct.pack("HHHH", 30, 100, 0, 0))
        process = subprocess.Popen(
            command or ["bash", str(self.repo / "scripts" / name)],
            stdin=slave, stdout=slave, stderr=slave, cwd=self.root, env=self.env,
        )
        os.close(slave)
        output = b""
        sent = False
        deadline = time.monotonic() + 10
        try:
            while time.monotonic() < deadline:
                if select.select([master], [], [], 0.1)[0]:
                    try:
                        chunk = os.read(master, 65536)
                    except OSError:
                        break
                    if not chunk:
                        break
                    output += chunk
                    if not sent and (b"Choices " in output or b"Destination: " in output or b"Backup mode: " in output):
                        os.write(master, keys)
                        sent = True
                if process.poll() is not None:
                    # Drain remaining output before checking the result.
                    while select.select([master], [], [], 0)[0]:
                        try:
                            output += os.read(master, 65536)
                        except OSError:
                            break
                    break
            self.assertIsNotNone(process.poll(), output.decode(errors="replace"))
            self.assertEqual(process.wait(), expected_exit, output.decode(errors="replace"))
            return output.decode(errors="replace")
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            os.close(master)

    def test_install_multiple_and_backup(self):
        claude = self.home / ".claude/CLAUDE.md"
        self.write(claude, "old Claude")
        # No repository files or helper scripts are available to the installer.
        (self.repo / "AGENTS.md").unlink()
        (self.repo / "scripts/common.sh").unlink()
        output = self.run_script("install-agents.sh", b"4\n1\ny\n")
        self.assertIn(str(claude), output)
        for relative in (".claude/CLAUDE.md", ".codex/AGENTS.md", ".config/opencode/AGENTS.md"):
            self.assertEqual((self.home / relative).read_text(), "remote instructions\n")
        backups = list(claude.parent.glob("CLAUDE.md.backup-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "old Claude")
        log = (self.root / "curl.log").read_text().splitlines()
        self.assertEqual(log[0], "https://raw.githubusercontent.com/lioqing/.agents/test-ref/AGENTS.md")
        self.assertFalse(Path(log[1]).parent.exists(), "download temporary directory is cleaned up")

    def test_decline_and_cancel(self):
        claude = self.home / ".claude/CLAUDE.md"
        self.write(claude, "unchanged")
        self.run_script("install-agents.sh", b"1\n1\nn\n")
        self.assertEqual(claude.read_text(), "unchanged")
        self.run_script("install-agents.sh", b"q\n")
        self.assertFalse((self.home / ".codex").exists())

    def test_remote_execution_keeps_stdin_available(self):
        script = (self.repo / "scripts/install-agents.sh").read_text()
        destination = self.home / "custom path/instructions.md"
        output = self.run_script(
            "install-agents.sh", f"invalid\n5\n{destination}\n1\n".encode(),
            command=["bash", "-c", script],
        )
        self.assertIn("Enter a number from 1 to 6", output)
        self.assertEqual(destination.read_text(), "remote instructions\n")
        self.assertIn("No existing instruction files found", output)

    def test_install_without_backup_lists_all_existing_destinations(self):
        destinations = (self.home / ".claude/CLAUDE.md", self.home / ".codex/AGENTS.md")
        for destination in destinations:
            self.write(destination, "old instructions")
        output = self.run_script("install-agents.sh", b"4\n2\ny\ny\n")
        for destination in destinations:
            self.assertIn(str(destination), output)
            self.assertEqual(destination.read_text(), "remote instructions\n")
            self.assertEqual(list(destination.parent.glob("*.backup-*")), [])

    def test_install_explicit_destination_backup_menu(self):
        destination = self.home / "custom path/AGENTS.md"
        self.write(destination, "old instructions")
        command = ["bash", str(self.repo / "scripts/install-agents.sh"), str(destination)]
        output = self.run_script("install-agents.sh", b"invalid\n2\nn\n", command=command)
        self.assertIn("Enter a number from 1 to 3", output)
        self.assertIn(str(destination), output)
        self.assertEqual(destination.read_text(), "old instructions")
        self.run_script("install-agents.sh", b"2\ny\n", command=command)
        self.assertEqual(destination.read_text(), "remote instructions\n")
        self.assertEqual(list(destination.parent.glob("*.backup-*")), [])
        self.write(destination, "backup me")
        self.run_script("install-agents.sh", b"1\ny\n", command=command)
        backups = list(destination.parent.glob("*.backup-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "backup me")

    def test_install_backup_mode_cancel_changes_nothing(self):
        destination = self.home / ".codex/AGENTS.md"
        self.write(destination, "unchanged")
        self.run_script("install-agents.sh", b"4\nq\n")
        self.assertEqual(destination.read_text(), "unchanged")
        self.assertEqual(list(destination.parent.glob("*.backup-*")), [])
        self.assertFalse((self.home / ".claude").exists())
        self.assertFalse((self.root / "curl.log").exists())
        command = ["bash", str(self.repo / "scripts/install-agents.sh"), str(destination)]
        self.run_script("install-agents.sh", b"3\n", command=command)
        self.assertFalse((self.root / "curl.log").exists())

    def test_install_backup_mode_eof_cancels_without_downloading(self):
        destination = self.home / "missing/AGENTS.md"
        result = subprocess.run(
            ["bash", str(self.repo / "scripts/install-agents.sh"), str(destination)],
            input="", text=True, capture_output=True, env=self.env,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Cancelled", result.stdout)
        self.assertFalse(destination.parent.exists())
        self.assertFalse((self.root / "curl.log").exists())

    def test_install_backup_flags_skip_menus(self):
        destination = self.home / "flag path/AGENTS.md"
        for flag in ("--backup", "--no-backup"):
            with self.subTest(flag=flag):
                self.write(destination, "flag original")
                result = subprocess.run(
                    ["bash", str(self.repo / "scripts/install-agents.sh"), flag, str(destination)],
                    input="yes\n", text=True, capture_output=True, env=self.env,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertNotIn("Backup mode:", result.stderr)
                self.assertNotIn("Destination:", result.stderr)
                self.assertEqual(destination.read_text(), "remote instructions\n")
                backups = list(destination.parent.glob("*.backup-*"))
                self.assertEqual(len(backups), int(flag == "--backup"))
                for backup in backups:
                    self.assertEqual(backup.read_text(), "flag original")
                    backup.unlink()

        self.write(destination, "declined")
        result = subprocess.run(
            ["bash", str(self.repo / "scripts/install-agents.sh"), str(destination), "--no-backup"],
            input="no\n", text=True, capture_output=True, env=self.env,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(destination.read_text(), "declined")
        self.assertEqual(list(destination.parent.glob("*.backup-*")), [])

    def test_install_backup_flag_keeps_destination_menu(self):
        destination = self.home / ".codex/AGENTS.md"
        self.write(destination, "flag original")
        output = self.run_script(
            "install-agents.sh", b"2\ny\n",
            command=["bash", str(self.repo / "scripts/install-agents.sh"), "--no-backup"],
        )
        self.assertIn("Destination:", output)
        self.assertNotIn("Backup mode:", output)
        self.assertEqual(destination.read_text(), "remote instructions\n")
        self.assertEqual(list(destination.parent.glob("*.backup-*")), [])

    def test_install_backup_flag_new_destination_and_option_terminator(self):
        destination = self.root / "--instructions.md"
        result = subprocess.run(
            ["bash", str(self.repo / "scripts/install-agents.sh"), "--backup", "--", destination.name],
            input="", text=True, capture_output=True, env=self.env, cwd=self.root,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(destination.read_text(), "remote instructions\n")
        self.assertFalse((self.root / "curl.log").read_text().splitlines()[-1] == "")
        self.assertEqual(list(self.root.glob("*.backup-*")), [])

    def test_install_invalid_arguments_change_nothing(self):
        destination = self.home / "flag path/AGENTS.md"
        self.write(destination, "unchanged")
        for arguments in (
            ["--backup", "--no-backup", str(destination)],
            ["--no-backup", "--backup", str(destination)],
            ["--unknown", str(destination)],
            ["--backup", str(destination), "extra.md"],
            ["--no-backup", ""],
        ):
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    ["bash", str(self.repo / "scripts/install-agents.sh"), *arguments],
                    input="", text=True, capture_output=True, env=self.env,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(destination.read_text(), "unchanged")
                self.assertFalse((self.root / "curl.log").exists())
                self.assertEqual(list(destination.parent.glob("*.backup-*")), [])

    def test_download_failure_and_empty_response_leave_destinations_alone(self):
        destination = self.home / ".codex/AGENTS.md"
        self.write(destination, "unchanged")
        for overrides in ({"FAKE_CURL_EXIT": "22"}, {"FAKE_CURL_EMPTY": "1"}):
            result = subprocess.run(
                ["bash", str(self.repo / "scripts/install-agents.sh"), str(destination)],
                input="1\nyes\n", text=True, capture_output=True, env=dict(self.env, **overrides),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(destination.read_text(), "unchanged")
            self.assertEqual(list(destination.parent.glob("*.backup-*")), [])

    def test_links_and_directories_are_not_replaced(self):
        original = self.root / "original.md"
        self.write(original, "unchanged")
        for name, target in (("linked.md", original), ("dangling.md", self.root / "missing")):
            destination = self.home / name
            destination.symlink_to(target)
            result = subprocess.run(
                ["bash", str(self.repo / "scripts/install-agents.sh"), str(destination)],
                input="yes\n", text=True, capture_output=True, env=self.env,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(destination.is_symlink())
        result = subprocess.run(
            ["bash", str(self.repo / "scripts/install-agents.sh"), str(self.home)],
            input="yes\n", text=True, capture_output=True, env=self.env,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(original.read_text(), "unchanged")

    def test_single_source_and_missing_disabled(self):
        self.write(self.home / ".codex/AGENTS.md", "Codex source")
        # Enter on missing Claude must not select it. Move down to Codex.
        output = self.run_script("import-agents.sh", b"\n\x1b[B\ny\n")
        self.assertIn("unavailable: file missing", output)
        self.assertEqual((self.repo / "AGENTS.md").read_text(), "Codex source")
        self.assertEqual(len(list(self.repo.glob("AGENTS.md.backup-*"))), 1)

    def test_skill_conflicts_links_and_assets(self):
        source = self.home / ".agents/skills"
        self.write(source / "alpha/SKILL.md", "alpha")
        self.write(source / "alpha/.hidden", "hidden")
        self.write(source / "alpha/assets/file [1].txt", "asset")
        self.write(source / "conflict/SKILL.md", "conflict")
        self.write(source / "invalid/not-a-skill.txt", "invalid")
        self.write(self.repo / "skills/conflict", "leave alone")
        (source / "linked").symlink_to(source / "alpha", target_is_directory=True)
        # Select alpha and linked; Space on the conflicting entry is ignored.
        output = self.run_script("import-skills.sh", b" \x1b[B \x1b[B \n\n")
        self.assertIn("unavailable: name already exists", output)
        self.assertEqual((self.repo / "skills/conflict").read_text(), "leave alone")
        self.assertEqual((self.repo / "skills/alpha/.hidden").read_text(), "hidden")
        self.assertEqual((self.repo / "skills/linked/assets/file [1].txt").read_text(), "asset")
        self.assertFalse((self.repo / "skills/linked").is_symlink())
        self.assertFalse((self.repo / "skills/invalid").exists())
        self.assertTrue((source / "alpha/SKILL.md").exists())
        self.assertTrue((source / "linked").is_symlink())
        self.assertIn("npx skills add lioqing/.agents --global", output)
        self.assertIn("No available choices", self.run_script("import-skills.sh", b""))

    def test_skill_move_and_link_safety(self):
        source = self.home / ".agents/skills"
        self.write(source / "alpha/SKILL.md", "alpha")
        self.write(source / "alpha/.hidden", "hidden")
        external = self.home / "external assets"
        self.write(external / "asset.txt", "asset")
        (source / "alpha/assets").symlink_to(external, target_is_directory=True)
        (source / "linked").symlink_to(source / "alpha", target_is_directory=True)
        output = self.run_script("import-skills.sh", b" \x1b[B \n\x1b[B\n")
        self.assertFalse((source / "alpha").exists())
        self.assertFalse((source / "linked").is_symlink())
        self.assertEqual((external / "asset.txt").read_text(), "asset")
        for name in ("alpha", "linked"):
            self.assertEqual((self.repo / f"skills/{name}/.hidden").read_text(), "hidden")
            self.assertEqual((self.repo / f"skills/{name}/assets/asset.txt").read_text(), "asset")
        self.assertIn("commit and push", output)
        self.assertIn("npx skills add lioqing/.agents --global", output)

    def test_skill_move_only_link_preserves_target(self):
        source = self.home / ".agents/skills/linked"
        target = self.home / "external skill"
        self.write(target / "SKILL.md", "external")
        source.parent.mkdir(parents=True)
        source.symlink_to(target, target_is_directory=True)
        self.run_script("import-skills.sh", b" \n\x1b[B\n")
        self.assertFalse(source.is_symlink())
        self.assertEqual((target / "SKILL.md").read_text(), "external")
        self.assertEqual((self.repo / "skills/linked/SKILL.md").read_text(), "external")

    def test_skill_mode_cancel_changes_nothing(self):
        source = self.home / ".agents/skills/alpha/SKILL.md"
        self.write(source, "alpha")
        self.run_script("import-skills.sh", b" \nq")
        self.assertEqual(source.read_text(), "alpha")
        self.assertFalse((self.repo / "skills").exists())

    def test_skill_move_copy_failure_preserves_all_sources(self):
        source = self.home / ".agents/skills"
        self.write(source / "alpha/SKILL.md", "alpha")
        self.write(source / "broken/SKILL.md", "broken")
        (source / "broken/loop").symlink_to(source / "broken", target_is_directory=True)
        self.run_script("import-skills.sh", b" \x1b[B \n\x1b[B\n", expected_exit=1)
        self.assertEqual((source / "alpha/SKILL.md").read_text(), "alpha")
        self.assertEqual((source / "broken/SKILL.md").read_text(), "broken")

    def test_paging_and_escape(self):
        for i in range(12):
            self.write(self.home / f".agents/skills/skill-{i:02d}/SKILL.md", str(i))
        output = self.run_script("import-skills.sh", b"\x1b[B" * 10 + b" \n\n")
        self.assertIn("Choices 11-12 of 12", output)
        self.assertEqual((self.repo / "skills/skill-10/SKILL.md").read_text(), "10")
        self.run_script("import-skills.sh", b"\x1b")
        self.assertFalse((self.repo / "skills/skill-00").exists())

    def test_install_eof_cancels_without_downloading(self):
        result = subprocess.run(
            ["bash", str(self.repo / "scripts/install-agents.sh")],
            input="", text=True, capture_output=True,
            env=self.env,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Cancelled", result.stdout)
        self.assertFalse((self.root / "curl.log").exists())

    def test_import_redirected_terminal_is_rejected(self):
        result = subprocess.run(
            ["bash", str(self.repo / "scripts/import-agents.sh")],
            input="", text=True, capture_output=True, env=self.env,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("interactive terminal", result.stderr)


if __name__ == "__main__":
    unittest.main()
