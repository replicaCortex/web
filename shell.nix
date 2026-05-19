{
  pkgs ? import <nixpkgs> { },
}:
pkgs.mkShell {
  buildInputs = with pkgs; [
    kind
    kubectl
    k9s
  ];

  shellHook = "";
}
