import os
import sys
import click
from cffconvert.cli.check_early_exits import check_early_exits
from cffconvert.cli.create_citation import create_citation
from cffconvert.cli.validate_or_write_output import DEFAULT_OUTPUT_FILES
from cffconvert.cli.validate_or_write_output import OUTPUT_FORMATS
from cffconvert.cli.validate_or_write_output import validate_or_write_output


def parse_output_format(ctx, _param, value):
    parsed = []
    for item in value:
        outputformat, separator, outfile = item.partition("=")
        if outputformat not in OUTPUT_FORMATS:
            raise click.BadParameter(f"{outputformat!r} is not one of {', '.join(OUTPUT_FORMATS)}")
        if separator and not outfile:
            raise click.BadParameter("output path cannot be empty")
        parsed.append((outputformat, outfile or DEFAULT_OUTPUT_FILES[outputformat]))
    return tuple(parsed)


options = {
    "infile": {
        "type": click.Path(),
        "default": None,
        "help": "Path to the CITATION.cff input file. If this option is omitted" +
                f", '.{os.sep}CITATION.cff' is used."
    },
    "outfile": {
        "type": click.Path(),
        "default": None,
        "help": "Path to the output file."
    },
    "outputformat": {
        "type": click.Choice(OUTPUT_FORMATS),
        "default": None,
        "help": "Output format."
    },
    "outputformats": {
        "multiple": True,
        "callback": parse_output_format,
        "metavar": "FORMAT[=PATH]",
        "help": "Write an output format to a file. Can be used multiple times. "
                "Uses default output paths when PATH is omitted."
    },
    "url": {
        "type": str,
        "default": None,
        "help": "URL to the CITATION.cff input file."
    },
    "show_help": {
        "is_flag": True,
        "flag_value": True,
        "default": False,
        "help": "Show help and exit."
    },
    "show_trace": {
        "is_flag": True,
        "flag_value": True,
        "default": False,
        "help": "Show error trace."
    },
    "validate_only": {
        "is_flag": True,
        "default": False,
        "help": "Validate the CITATION.cff file and exit."
    },
    "version": {
        "is_flag": True,
        "default": False,
        "help": "Print version and exit."
    },
    "verbose": {
        "is_flag": True,
        "default": False,
        "help": "Control output verbosity."
    }
}
epilog = """If this program is useful to you, consider giving it a star on GitHub:
https://github.com/SciCodes/cffconvert"""


@click.command(epilog=epilog)
@click.option("-i", "--infile", "infile", **options["infile"])
@click.option("-o", "--outfile", "outfile", **options["outfile"])
@click.option("-f", "--format", "outputformat", **options["outputformat"])
@click.option("-O", "--output", "outputformats", **options["outputformats"])
@click.option("-u", "--url", "url", **options["url"])
@click.option("-h", "--help", "show_help", **options["show_help"])
@click.option("--show-trace", "show_trace", **options["show_trace"])
@click.option("--validate", "validate_only", **options["validate_only"])
@click.option("--version", "version", **options["version"])
@click.option("--verbose", "verbose", **options["verbose"])
# pylint: disable=too-many-arguments
def cli(infile, outfile, outputformat, outputformats, url, show_help, show_trace, validate_only, version, verbose):
    """Command line program to validate and convert CITATION.cff files."""

    check_early_exits(show_help, version)

    if show_trace is False:
        # show elaborate error details if something goes wrong
        sys.tracebacklimit = 0

    # if user didn't specify a filename or a url, apply default filename
    if infile is None and url is None:
        infile = "CITATION.cff"

    # load the citation metadata from the specified source and create a Python object representation of it
    citation = create_citation(infile, url)

    # either validate and exit, or convert to the selected output format
    validate_or_write_output(outfile, outputformat, outputformats, validate_only, citation, verbose)
