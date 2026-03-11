{
  pkgs ? import <nixpkgs> { },
}:
pkgs.mkShell {
  buildInputs = with pkgs; [
    uv
  ];

  shellHook = "
  source .venv/bin/activate.fish
  ";
}
