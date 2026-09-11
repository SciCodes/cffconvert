import click
from jsonschema.exceptions import ValidationError as JsonschemaSchemaError
from pykwalify.errors import SchemaError as PykwalifySchemaError


CONVERTERS = {
    "apalike": "as_apalike",
    "bibtex": "as_bibtex",
    "cff": "as_cff",
    "codemeta": "as_codemeta",
    "endnote": "as_endnote",
    "ris": "as_ris",
    "schema.org": "as_schemaorg",
    "zenodo": "as_zenodo",
}
OUTPUT_FORMATS = tuple(CONVERTERS)

DEFAULT_OUTPUT_FILES = {
    "apalike": "_citation.txt",
    "bibtex": "_citation.bib",
    "cff": "_citation.cff",
    "codemeta": "codemeta.json",
    "endnote": "_citation.enw",
    "ris": "_citation.ris",
    "schema.org": "schemaorg.json",
    "zenodo": ".zenodo.json",
}


def render_output(citation, outputformat):
    return getattr(citation, CONVERTERS[outputformat])()


def write_output(outfile, outstr):
    if outfile is None:
        print(outstr, end="")
    else:
        with open(outfile, "w", encoding="utf8") as fid:
            fid.write(outstr)


def validate_for_conversion(citation, verbose):
    try:
        citation.validate(verbose)
    except (PykwalifySchemaError, JsonschemaSchemaError):
        print(f"'{citation.src}' does not pass validation. Conversion aborted.")
        ctx = click.get_current_context()
        ctx.exit(1)


def validate_or_write_output(outfile, outputformat, outputformats, validate_only, citation, verbose=True):
    condition = (validate_only, outputformat is not None or bool(outputformats))
    if condition == (True, False):
        # just validate, there is no target outputformat
        citation.validate(verbose)
        print(f"Citation metadata are valid according to schema version {citation.cffversion}.")
    elif condition == (True, True):
        # just validate, ignore the target outputformat
        citation.validate(verbose)
        print(f"Ignoring output format. Citation metadata are valid according to schema version {citation.cffversion}.")
    elif condition == (False, False):
        # user hasn't indicated what they want
        print("Indicate whether you want to validate or convert the citation metadata.")
    elif condition == (False, True):
        # validate the input, then write to target outputformat
        validate_for_conversion(citation, verbose)
        outputs = []
        if outputformat is not None:
            outputs.append((outfile, render_output(citation, outputformat)))
        for fmt, fmt_outfile in outputformats:
            outputs.append((fmt_outfile, render_output(citation, fmt)))
        for output_path, output_text in outputs:
            write_output(output_path, output_text)
    else:
        # shouldn't happen
        raise ValueError("Something went wrong validating or writing the output")
