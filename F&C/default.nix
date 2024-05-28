{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python310
    pkgs.python310Packages.pip
    pkgs.python310Packages.virtualenv
  ];

  shellHook = ''
    if [ ! -d ".venv" ]; then
      virtualenv .venv
    fi
    source .venv/bin/activate
    pip install --upgrade pip
    pip install git+https://github.com/dponcedeleonf/instantneo.git
    pip install git+https://github.com/dponcedeleonf/instantneo.git@desarrollo
    pip install python-dotenv
    pip install PyPDF2
    pip install flask PyMuPDF pillow
  '';
}