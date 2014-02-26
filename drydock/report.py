"""End of run reports."""
__author__ = 'Taylor \"Nekroze\" Lawson'


class Report(object):
    def __init__(self):
        self.containers = {"success": {}, "failed": {}}
        self.paths = []
        self.commands = {"success": {}, "failed": {}}

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
            output.append("    {} containers {}.".format(
                success, "deleted" if remove else "created"))
            output.append("    >" + ', '.join(
                name for name in self.containers["success"].keys()))
        if failed:
            output.append("    {} containers to be {}.".format(
                failed, "deleted" if remove else "created"))
            for name, command in self.containers["failed"].items():
                output.append("    >{}: {}".format(name, command))

        output.append("")

        success = len(self.commands["success"].keys())
        failed = len(self.commands["failed"].keys())
        if success:
            output.append("    {} commands succeeded.".format(success))
            for desc in self.commands["success"].values():
                output.append("    >" + desc)
        if failed:
            output.append("    {} commands failed.".format(failed))
            for desc, command in self.commands["failed"].items():
                output.append("    >{}: {}".format(desc, command))

        output.append("")

        if len(self.paths):
            output.append("    {} paths {}.".format(
                len(self.paths), "deleted" if remove else "written"))

        return '\n'.join(output)