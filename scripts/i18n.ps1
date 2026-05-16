param(
    [ValidateSet("extract", "compile", "all")]
    [string]$Action = "all"
)

$ErrorActionPreference = "Stop"

function Run-Extract {
    python manage.py makemessages -l sr_Latn --ignore venv --ignore staticfiles --ignore media
}

function Run-Compile {
    python manage.py compilemessages
}

switch ($Action) {
    "extract" { Run-Extract }
    "compile" { Run-Compile }
    "all" {
        Run-Extract
        Run-Compile
    }
}
