"""Runnable source for Tutorial Lesson 12.

Presented to learners as **Lesson 11**: lesson_11_llm_tasks.py just imports
and calls main() from this file. See that file for why the numbers differ.
Run from the repository root.
"""

import json
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from dagon import Workflow
from dagon.task import DagonTask, TaskType


class MockChatHandler(BaseHTTPRequestHandler):
    """A deterministic, local subset of the Chat Completions protocol.

    Standing up a throwaway HTTP server keeps this lesson runnable offline
    and without a real API key, while still exercising the same
    TaskType.LLM code path a real provider endpoint would use.
    """

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            self.send_error(404)
            return
        raw_body = self.rfile.read(int(self.headers["Content-Length"]))
        request = json.loads(raw_body.decode("utf-8"))
        content = request["messages"][-1]["content"]
        message = {"role": "assistant", "content": "Mock summary: " + content}
        response = {"choices": [{"message": message}]}
        payload = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, _format, *_args):
        pass  # silence the default per-request access log


def main():
    # Port 0 asks the OS for any free local port, avoiding clashes with
    # anything else already running on the machine.
    server = ThreadingHTTPServer(("127.0.0.1", 0), MockChatHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with tempfile.TemporaryDirectory(prefix="dagon-llm-lesson-") as scratch:
            config = {
                "batch": {"scratch_dir_base": scratch, "run_base": "", "threads": "1"},
                "dagon_service": {"use": "False", "route": "http://localhost:57000"},
                "ftp_pub": {"ip": "localhost", "user": "anonymous", "password": ""},
                "slurm": {"partition": ""},
                # An "llm.<provider>" section registers an LLM provider named
                # <provider>; DagonTask(..., provider="local_mock") below
                # selects it and points TaskType.LLM at our mock server.
                "llm.local_mock": {
                    "endpoint": "http://127.0.0.1:%s" % server.server_port,
                    "api_key": "example-key-not-a-secret",
                    "model": "mock-chat",
                },
            }
            workflow = Workflow("Lesson12", config=config)
            prepare_command = (
                "mkdir -p output; "
                "printf 'temperature increased by 1.2 C' > output/report.txt"
            )
            prepare_task = DagonTask(TaskType.BATCH, "prepare_report", prepare_command)
            workflow.add_task(prepare_task)
            # TaskType.LLM's "command" is a chat request body, not a shell
            # string. input_files stages a workflow:/// file (lesson 03) and
            # lets "{report}" in the message content be substituted with its
            # contents before the request is sent.
            request_body = {
                "messages": [
                    {"role": "user", "content": "Summarize this report: {report}"}
                ]
            }
            summarize = DagonTask(
                TaskType.LLM,
                "summarize_report",
                request_body,
                provider="local_mock",
                input_files={"report": "workflow:///prepare_report/output/report.txt"},
            )
            workflow.add_task(summarize)
            workflow.run()
            response = Path(summarize.working_dir, "response.json")
            data = json.loads(response.read_text(encoding="utf-8"))
            summary = data["choices"][0]["message"]["content"]
            expected = (
                "Mock summary: Summarize this report: temperature increased by 1.2 C"
            )
            assert summary == expected
            print(response.read_text(encoding="utf-8"))
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
