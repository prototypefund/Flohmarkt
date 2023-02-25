{
  description = "Flohmarkt development flake";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.11";

  outputs = { self, nixpkgs }: {
    defaultPackage.x86_64-linux = 
    with import <nixpkgs> { system = "x86_64-linux" }
    buildPythonpackage rec {
      pname = "flohmarkt";
      src = ./flohmarkt;
    }
  }
}
