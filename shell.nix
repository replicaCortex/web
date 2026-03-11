{
  pkgs ? import <nixpkgs> { },
}:
pkgs.mkShell {
  buildInputs = with pkgs; [
    uv
  ];

  LD_LIBRARY_PATH = "$LD_LIBRARY_PATH:${pkgs.stdenv.cc.cc.lib.outPath}/lib:$LD_LIBRARY_PATH";

  shellHook = "
  ";
}
