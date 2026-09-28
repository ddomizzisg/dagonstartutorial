"""Runnable source for Tutorial Lesson 13.

Presented to learners as **Lesson 10**: lesson_10_web_tasks.py just imports
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


class EchoHandler(BaseHTTPRequestHandler):
    """Local endpoint used to demonstrate a multipart web task.

    Standing up a throwaway HTTP server keeps this lesson runnable offline,
    while still exercising the same TaskType.WEB code path a real HTTP API
    would use.
    """

    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        received = "sample" in body.decode("utf-8")
        reply = json.dumps({"received": received}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(reply)))
        self.end_headers()
        self.wfile.write(reply)

    def log_message(self, _format, *_args):
        pass  # silence the default per-request access log


def main():
    # Port 0 asks the OS for any free local port, avoiding clashes with
    # anything else already running on the machine.
    server = ThreadingHTTPServer(("127.0.0.1", 0), EchoHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with tempfile.TemporaryDirectory(prefix="dagon-web-lesson-") as scratch:
            config = {
                "batch": {"scratch_dir_base": scratch, "run_base": "", "threads": "1"},
                "dagon_service": {"use": "False", "route": "http://localhost:57000"},
                "ftp_pub": {"ip": "localhost", "user": "anonymous", "password": ""},
                "slurm": {"partition": ""},
            }
            workflow = Workflow("Lesson13", config=config)
            workflow.add_task(DagonTask(
                TaskType.BATCH,
                "prepare",
                "mkdir -p output; printf sample > output/data.txt",
            ))
            # TaskType.WEB's "command" is a request spec, not a shell
            # string: method/url/multipart describe an HTTP call, and
            # "outputs" maps response parts (body, metadata) to files
            # DAGon* writes so downstream tasks can read them via
            # workflow:/// staging (lesson 03), like "consume" does below.
            upload = DagonTask(
                TaskType.WEB,
                "upload",
                {
                    "method": "POST",
                    "url": "http://127.0.0.1:%s/upload" % server.server_port,
                    "multipart": {
                        "dataset": {
                            "file": "workflow:///prepare/output/data.txt",
                            "content_type": "text/plain",
                        }
                    },
                    "expected_status": 200,
                    "outputs": {"body": "reply.json", "metadata": "request.json"},
                },
            )
            workflow.add_task(upload)
            workflow.add_task(DagonTask(
                TaskType.BATCH,
                "consume",
                "cat workflow:///upload/outputs/reply.json",
            ))
            workflow.run()
            reply_path = Path(upload.working_dir, "outputs", "reply.json")
            assert json.loads(reply_path.read_text()) == {"received": True}
            result_path = Path(upload.working_dir, ".dagon", "web_result.json")
            web_result = json.loads(result_path.read_text())
            assert web_result["status_code"] == 200
            assert web_result["method"] == "POST"
            print(reply_path.read_text())
            print(result_path.read_text())
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
