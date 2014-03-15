"""End of run reports."""
__author__ = 'Taylor \"Nekroze\" Lawson'
import sys


class Report(object):
    def __init__(self):
        self.containers = {"success": {}, "failed": {}}
        self.paths = []
        self.commands = {"success": {}, "failed": {}}

    def exit(self):
        """Exit the program with the appropriate code based on the report."""
        if self.containers["failed"] or self.commands["failed"]:
            sys.exit(1)
        else:
            sys.exit(0)

    def container(self, name, command, code):
        """Report on the status of a container"""
        key = "success" if code == 0 else "failed"
        self.containers[key][name] = command

    def path(self, path):
        """Report on the status of a path"""
        self.paths.append(path)

    def command(self, description, command, code):
        """Report on the status of a command"""
        key = "success" if code == 0 else "failed"
        self.commands[key][description] = command

    def render(self, remove=False):
        """
        Render the current state of this report.

        If the ``remove`` argument is true then a removal report will be
        rendered.
        """
        output = ["DryDock Report:"]

        success = len(self.containers["success"].keys())
        failed = len(self.containers["failed"].keys())
        if success:
            output.append("    {} container(s) {}.".format(
                success, "deleted" if remove else "created"))
            output.append("    >" + ', '.join(
                name for name in self.containers["success"].keys()))
        if failed:
            output.append("    {} container(s) failed to be {}.".format(
                failed, "deleted" if remove else "created"))
            for name, command in self.containers["failed"].items():
                output.append("    >{}: {}".format(name, command))

        if success or failed:
            output.append("")

        success = len(self.commands["success"].keys())
        failed = len(self.commands["failed"].keys())
        if success:
            output.append("    {} command(s) succeeded.".format(success))
        if failed:
            output.append("    {} command(s) failed.".format(failed))
            for desc, command in self.commands["failed"].items():
                output.append("    >{}: {}".format(desc, command))

        if success or failed:
            output.append("")

        if len(self.paths):
            output.append("    {} path(s) {}.".format(
                len(self.paths), "deleted" if remove else "written"))
            for path in self.paths:
                output.append("    >" + path)

        return '\n'.join(output)